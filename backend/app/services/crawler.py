import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from backend.app.config import settings
from backend.app.core.logger import get_logger

logger = get_logger("Crawler")

class EthicalCrawler:
    def __init__(self):
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }

    async def fetch_and_parse(self, url: str) -> Optional[Dict[str, Any]]:
        domain = urlparse(url).netloc
        try:
            async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url} (status {response.status_code})")
                    return None
                
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                
                # Strip out noise elements
                for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
                    element.decompose()
                
                # Title
                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                if not title:
                    h1 = soup.find("h1")
                    title = h1.get_text(strip=True) if h1 else domain
                
                # Headings
                headings = []
                for h in soup.find_all(["h1", "h2", "h3"]):
                    text = h.get_text(strip=True)
                    if text and len(text) > 3:
                        headings.append(f"{h.name.upper()}: {text}")
                
                # Main body text
                paragraphs = []
                for p in soup.find_all("p"):
                    p_text = p.get_text(strip=True)
                    if len(p_text) > 35: # Exclude tiny cookie notices
                        paragraphs.append(p_text)
                
                clean_text = "\n\n".join(paragraphs)
                
                if len(clean_text) < 100:
                    # Fallback to general text if paragraphs were sparse
                    clean_text = soup.get_text(separator="\n", strip=True)
                
                # Publication date extraction (if present in meta tags)
                pub_date = None
                date_meta = soup.find("meta", attrs={"property": "article:published_time"}) or \
                            soup.find("meta", attrs={"name": "publication_date"}) or \
                            soup.find("meta", attrs={"name": "date"})
                if date_meta and date_meta.get("content"):
                    pub_date = str(date_meta["content"])[:10]
                
                return {
                    "url": url,
                    "domain": domain,
                    "title": title,
                    "headings": headings,
                    "clean_text": clean_text[:12000], # Cap to avoid gigantic memory usage
                    "publication_date": pub_date or "2024-Q1"
                }
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
