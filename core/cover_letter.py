# core/cover_letter.py
import anthropic
from config import ANTHROPIC_API_KEY, APPLICANT_PROFILE, APPLICANT_NAME

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client

def generate(job: dict) -> str:
    """Generate cover letter yang dipersonalisasi untuk setiap job."""
    if not ANTHROPIC_API_KEY:
        return _fallback_cover_letter(job)

    prompt = f"""
Kamu adalah career coach profesional yang membantu developer freelance Indonesia melamar kerja remote internasional.

PROFIL PELAMAR:
{APPLICANT_PROFILE}

LOWONGAN:
- Posisi  : {job.get('title','')}
- Company : {job.get('company','')}
- Tags    : {job.get('tags','')}
- Deskripsi (ringkas): {job.get('description','')[:800]}

TUGAS:
Tulis cover letter profesional dalam Bahasa Inggris untuk posisi ini.
Panjang: 3 paragraf (bukan lebih).

Paragraf 1: Opening kuat — tunjukkan antusias + relevansi skill terbesar untuk posisi ini.
Paragraf 2: Highlight 2-3 proyek/pencapaian konkret yang paling relevan dengan job ini.
Paragraf 3: Closing — ajak untuk interview, tunjukkan fleksibilitas timezone remote.

ATURAN:
- Jangan sebut "kurang pengalaman remote" — fokus ke skill & proyek
- Tone: professional tapi tidak kaku, percaya diri
- Tidak perlu header/Dear/Regards (nanti ditambah di email template)
- Tulis langsung isi 3 paragraf saja, tanpa intro atau preamble
"""

    try:
        msg = _get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"[CoverLetter] API error: {e}")
        return _fallback_cover_letter(job)

def _fallback_cover_letter(job: dict) -> str:
    """Cover letter template statis jika API tidak tersedia."""
    return f"""I am excited to apply for the {job.get('title','')} position at {job.get('company','')}. With 3+ years of experience in algorithmic trading systems, Python automation, and Web3 development, I am confident I can deliver exceptional results for your team.

My recent projects include building MQL5 Expert Advisors for gold scalping (XAUUSD) with auto-compound risk management, Python trading bots deployed on VPS, a DeFi LP agent for Solana's Meteora DLMM protocol, and a React-based meme coin scanner using the GeckoTerminal API. These projects demonstrate my ability to work across the full stack of trading automation and blockchain development.

I am fully available for remote work and comfortable collaborating across different timezones. I would love the opportunity to discuss how my technical background aligns with your needs. Thank you for your consideration.

Best regards,
{APPLICANT_NAME}"""
