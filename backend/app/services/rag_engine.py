import math
import re
import json
import hashlib
from typing import List, Dict, Any, Tuple

class RAGEngine:
    def __init__(self):
        self.stop_words = {
            "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
            "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
            "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
            "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
            "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
            "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
            "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
            "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
            "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
            "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
            "with", "would", "you", "your", "yours", "yourself", "yourselves"
        }

    def chunk_document(self, text: str, source_metadata: Dict[str, Any], chunk_size: int = 500, overlap: int = 80) -> List[Dict[str, Any]]:
        """Document-aware chunker that splits on paragraphs and preserves heading context."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_word_count = 0
        current_heading = source_metadata.get("title", "Overview")
        chunk_idx = 0

        for p in paragraphs:
            p_strip = p.strip()
            if not p_strip:
                continue

            # Detect headings
            if p_strip.startswith(("#", "H1:", "H2:", "H3:")) or (len(p_strip) < 70 and p_strip.endswith(":")):
                current_heading = p_strip.replace("#", "").strip()
                continue

            words = p_strip.split()
            word_len = len(words)

            if current_word_count + word_len > chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": chunk_text,
                    "token_count": len(chunk_text.split()),
                    "heading_path": current_heading,
                    "metadata": {
                        **source_metadata,
                        "heading": current_heading
                    }
                })
                chunk_idx += 1
                
                # Keep overlap words
                overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_words + words
                current_word_count = len(current_chunk)
            else:
                current_chunk.extend(words)
                current_word_count += word_len

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "chunk_index": chunk_idx,
                "content": chunk_text,
                "token_count": len(chunk_text.split()),
                "heading_path": current_heading,
                "metadata": {
                    **source_metadata,
                    "heading": current_heading
                }
            })

        return chunks

    def compute_embedding(self, text: str, dim: int = 128) -> List[float]:
        """
        Fast, zero-dependency subword feature embedding with L2 unit-normalization.
        Ensures immediate deterministic semantic vectors without heavyweight downloads.
        """
        tokens = re.findall(r"\w+", text.lower())
        vec = [0.0] * dim
        for token in tokens:
            # 3-gram hashing into vector dimensions
            for i in range(len(token) - 2):
                gram = token[i:i+3]
                h = int(hashlib.md5(gram.encode()).hexdigest(), 16) % dim
                vec[h] += 1.0

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        return sum(a * b for a, b in zip(v1, v2))

    def bm25_score(self, query: str, doc_text: str, avg_doc_len: float = 300.0, k1: float = 1.5, b: float = 0.75) -> float:
        """BM25 Lexical scoring for exact clinical and technical terms."""
        q_tokens = [w.lower() for w in re.findall(r"\w+", query) if w.lower() not in self.stop_words]
        doc_tokens = [w.lower() for w in re.findall(r"\w+", doc_text)]
        doc_len = len(doc_tokens)
        
        score = 0.0
        for token in q_tokens:
            tf = doc_tokens.count(token)
            if tf > 0:
                # BM25 term weighting
                idf = 1.8 # baseline IDF estimation
                num = tf * (k1 + 1)
                denom = tf + k1 * (1 - b + b * (doc_len / avg_doc_len))
                score += idf * (num / denom)
        return score

    def hybrid_retrieve(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 6) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion (RRF) between Dense Semantic & BM25 Lexical search.
        """
        if not chunks:
            return []

        q_vec = self.compute_embedding(query)

        # 1. Dense scoring
        dense_ranked = []
        for c in chunks:
            if "embedding" not in c:
                c["embedding"] = self.compute_embedding(c["content"])
            sim = self.cosine_similarity(q_vec, c["embedding"])
            dense_ranked.append((c, sim))
        dense_ranked.sort(key=lambda x: x[1], reverse=True)

        # 2. Lexical scoring
        lexical_ranked = []
        for c in chunks:
            score = self.bm25_score(query, c["content"])
            lexical_ranked.append((c, score))
        lexical_ranked.sort(key=lambda x: x[1], reverse=True)

        # 3. Reciprocal Rank Fusion (k=60)
        rrf_scores: Dict[int, float] = {}
        for rank, (c, _) in enumerate(dense_ranked):
            idx = c["chunk_index"]
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (60.0 + rank + 1))

        for rank, (c, _) in enumerate(lexical_ranked):
            idx = c["chunk_index"]
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (60.0 + rank + 1))

        # Re-sort chunks by RRF score
        chunk_map = {c["chunk_index"]: c for c in chunks}
        sorted_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)

        results = []
        for idx in sorted_indices[:top_k]:
            item = dict(chunk_map[idx])
            item["rrf_score"] = rrf_scores[idx]
            results.append(item)

        return results

    def compile_evidence_pack(self, top_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compiles clean, citation-ready evidence items with explicit [EVID-xxx] markers."""
        evidence_pack = []
        for i, chunk in enumerate(top_chunks, 1):
            tag = f"[EVID-{i:03d}]"
            content = chunk["content"]
            
            # Select most salient quote sentence
            sentences = re.split(r"(?<=[.!?])\s+", content)
            quote = sentences[0] if sentences else content[:150]
            for s in sentences:
                if any(w in s.lower() for w in ["ai", "clinical", "fhir", "fda", "interoperability", "model", "patient", "workflow"]):
                    quote = s.strip()
                    break

            meta = chunk.get("metadata", {})
            evidence_pack.append({
                "evidence_tag": tag,
                "claim_supported": f"Contextual evidence regarding {chunk.get('heading_path', 'Clinical AI')}",
                "verbatim_quote": quote,
                "source_title": meta.get("title", "Clinical Research Document"),
                "source_url": meta.get("url", "https://citiustech.com"),
                "source_tier": meta.get("source_type", "PEER_REVIEWED"),
                "confidence_score": round(chunk.get("rrf_score", 0.95) * 100, 2)
            })
        return evidence_pack
