# core/cover_letter.py — pakai Groq API (GRATIS)
import os, requests
from config import GROQ_API_KEY, APPLICANT_PROFILE, APPLICANT_NAME

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL    = "llama3-8b-8192"   # gratis, cepat, bagus untuk cover letter

def generate(job: dict) -> str:
    """Generate cover letter personal untuk setiap job pakai Groq (gratis)."""
    if not GROQ_API_KEY:
        return _fallback(job)

    prompt = f"""You are a professional career coach helping an Indonesian freelance developer apply for remote international jobs.

APPLICANT PROFILE:
{APPLICANT_PROFILE}

JOB:
- Position : {job.get('title','')}
- Company  : {job.get('company','')}
- Tags     : {job.get('tags','')}
- Description (brief): {job.get('description','')[:600]}

Write a professional cover letter in English. Exactly 3 paragraphs:
1. Strong opening — enthusiasm + most relevant skill for THIS specific job
2. 2-3 concrete projects/achievements most relevant to this job
3. Closing — invite interview, mention timezone flexibility for remote work

RULES:
- Do NOT mention lack of remote experience — focus on skills and projects
- Professional but not stiff, confident tone
- No header/Dear/Regards (added separately in email)
- Write only the 3 paragraphs, nothing else"""

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[CoverLetter] Groq error: {e}")
        return _fallback(job)

def _fallback(job: dict) -> str:
    return f"""I am excited to apply for the {job.get('title','')} position at {job.get('company','')}. With 3+ years of experience in algorithmic trading systems, Python automation, and Web3 development, I am confident I can deliver exceptional results for your team.

My recent projects include building MQL5 Expert Advisors for XAUUSD gold scalping with auto-compound risk management, Python trading bots deployed on VPS, a DeFi LP agent for Solana's Meteora DLMM protocol, and a React-based meme coin scanner using the GeckoTerminal API. These projects demonstrate my ability to work across the full stack of trading automation and blockchain development.

I am fully available for remote work and comfortable collaborating across different timezones. I would love the opportunity to discuss how my technical background aligns with your needs. Thank you for your consideration.

Best regards,
{APPLICANT_NAME}"""
