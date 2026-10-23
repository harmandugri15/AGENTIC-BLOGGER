import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import quote_plus
from backend.app.core.logger import get_logger

logger = get_logger("SearchService")

class SearchService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    async def search_duckduckgo(self, query: str, max_results: int = 4) -> List[Dict[str, str]]:
        """Zero-key ethical search via DuckDuckGo HTML endpoint."""
        results = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            async with httpx.AsyncClient(timeout=2.0, follow_redirects=True) as client:
                res = await client.post(url, data={"q": query}, headers=self.headers)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    links = soup.find_all("a", class_="result__snippet")
                    for a in links[:max_results]:
                        parent = a.find_parent("div", class_="result__body")
                        if parent:
                            title_elem = parent.find("a", class_="result__url") or parent.find("h2")
                            title = title_elem.get_text(strip=True) if title_elem else "Industry Analysis"
                            href = a.get("href", "")
                            snippet = a.get_text(strip=True)
                            
                            # Clean up DuckDuckGo redirect url if needed
                            if "uddg=" in href:
                                import urllib.parse
                                actual_url = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                            else:
                                actual_url = href
                                
                            if actual_url.startswith("http"):
                                results.append({
                                    "url": actual_url,
                                    "title": title,
                                    "snippet": snippet,
                                    "source_type": "COMPETITOR"
                                })
        except Exception as e:
            logger.warning(f"DuckDuckGo search encountered an issue: {e}")

        return results

    async def search_pubmed(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Retrieves real peer-reviewed scientific studies from NCBI PubMed E-Utilities."""
        results = []
        try:
            search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={quote_plus(query)}&retmode=json&retmax={max_results}"
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(search_url)
                if res.status_code == 200:
                    data = res.json()
                    id_list = data.get("esearchresult", {}).get("idlist", [])
                    
                    if id_list:
                        ids_str = ",".join(id_list)
                        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
                        sum_res = await client.get(summary_url)
                        if sum_res.status_code == 200:
                            sum_data = sum_res.json().get("result", {})
                            for pmid in id_list:
                                item = sum_data.get(pmid)
                                if item:
                                    title = item.get("title", "Clinical Study")
                                    pubdate = item.get("pubdate", "2024")
                                    journal = item.get("source", "PubMed Central")
                                    results.append({
                                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                        "title": title,
                                        "snippet": f"Published in {journal} ({pubdate}). Peer-reviewed biomedical study evaluating clinical and healthtech outcomes.",
                                        "source_type": "PUBMED",
                                        "publication_date": pubdate
                                    })
        except Exception as e:
            logger.warning(f"PubMed API search error: {e}")

        return results
