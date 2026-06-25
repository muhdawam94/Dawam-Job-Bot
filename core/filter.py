# core/filter.py
import re
from config import INCLUDE_KEYWORDS, EXCLUDE_KEYWORDS, MIN_SCORE

def _clean(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").lower()

def score_job(job: dict) -> int:
    """
    Score job 0-100 berdasarkan keyword matching.
    Title match  = 15 poin per kata
    Tag match    = 10 poin per kata
    Desc match   =  5 poin per kata
    Max cap      = 100
    """
    title = _clean(job.get("title", ""))
    tags  = _clean(job.get("tags", ""))
    desc  = _clean(job.get("description", ""))
    score = 0

    for kw in INCLUDE_KEYWORDS:
        kw_l = kw.lower()
        if kw_l in title: score += 15
        if kw_l in tags:  score += 10
        if kw_l in desc:  score +=  5

    return min(score, 100)

def has_exclusion(job: dict) -> bool:
    combined = _clean(job.get("title","") + " " + job.get("description",""))
    return any(ex.lower() in combined for ex in EXCLUDE_KEYWORDS)

def filter_jobs(jobs: list[dict]) -> list[dict]:
    results = []
    for job in jobs:
        if has_exclusion(job):
            continue
        s = score_job(job)
        if s >= MIN_SCORE:
            job["score"] = s
            results.append(job)
    # urutkan dari score tertinggi
    return sorted(results, key=lambda x: x["score"], reverse=True)
