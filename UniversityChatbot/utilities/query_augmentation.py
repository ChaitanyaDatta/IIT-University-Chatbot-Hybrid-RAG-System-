import json
import re
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

def _load_vocabulary() -> dict:
    for p in [
        Path(__file__).resolve().parent / "config" / "vocabulary.json",
        Path(__file__).resolve().parent.parent / "utilities" / "config" / "vocabulary.json",
    ]:
        if p.exists():
            with open(p) as f:
                return json.load(f)
    return {}

_VOCAB = _load_vocabulary()

# Domain-specific synonym expansions for BM25 query augmentation.
DOMAIN_SYNONYMS: Dict[str, Dict[str, List[str]]] = _VOCAB.get("domain_synonyms", {})


# Appends synonym expansions to a query, up to max_expansions new terms.
# Only adds synonyms that introduce vocabulary not already in the query.
def expand_query(query: str, domain: str, max_expansions: int = 3) -> str:
    if not query or not query.strip() or domain not in DOMAIN_SYNONYMS:
        return query

    synonyms_dict = DOMAIN_SYNONYMS[domain]
    query_lower = re.sub(r"[-_]", " ", query.lower())
    query_tokens = set(re.findall(r"\b\w+\b", query_lower))

    added_synonyms = []
    for key, syns in synonyms_dict.items():
        if re.search(r"\b" + re.escape(key) + r"\b", query_lower):
            for syn in syns:
                syn_words = set(re.findall(r"\b\w+\b", syn.lower()))
                if not syn_words.issubset(query_tokens):
                    added_synonyms.append(syn)
                    query_tokens.update(syn_words)
                    if len(added_synonyms) >= max_expansions:
                        break
        if len(added_synonyms) >= max_expansions:
            break

    return (query.strip() + " " + " ".join(added_synonyms)) if added_synonyms else query
