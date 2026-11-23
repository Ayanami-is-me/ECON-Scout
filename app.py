import html
import math
import re
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="Pixel Scouting HQ | Multi-Agent Football Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# Subtle Pitch Green Editorial CSS
# ==========================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
}
.stApp {
    background-color: #F3F6F4;
    background-image:
        radial-gradient(at 12% 4%, rgba(16, 185, 129, 0.08) 0px, transparent 42%),
        radial-gradient(at 88% 8%, rgba(5, 150, 105, 0.06) 0px, transparent 42%),
        linear-gradient(rgba(6, 95, 70, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(6, 95, 70, 0.03) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 32px 32px, 32px 32px;
    color: #0F172A;
}
header[data-testid="stHeader"] {
    background-color: rgba(243, 246, 244, 0.85);
}

/* Typography & Spacing */
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1180px;
}
h1, h2, h3, h4 {
    color: #0F172A !important;
    letter-spacing: -0.02em;
    font-weight: 700 !important;
}
p, li {
    color: #334155;
    line-height: 1.65;
}
label[data-testid="stWidgetLabel"] p {
    color: #475569 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

/* Subtle Sage Sidebar */
section[data-testid="stSidebar"] {
    background-color: #E8EFEA !important;
    border-right: 1px solid #D5E0D9 !important;
}

/* Unified Button Radius (8px) & Pitch Green Primary */
.stButton > button, .stDownloadButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"] {
    background-color: #065F46 !important;
    color: #FFFFFF !important;
    border: 1px solid #065F46 !important;
    box-shadow: 0 2px 6px rgba(6, 95, 70, 0.18) !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #047857 !important;
    border-color: #047857 !important;
}
.stButton > button[kind="secondary"], .stDownloadButton > button {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
}
.stButton > button[kind="secondary"]:hover, .stDownloadButton > button:hover {
    border-color: #065F46 !important;
    color: #065F46 !important;
    background-color: #F8FAF9 !important;
}

/* Inputs & Textareas */
.stTextArea textarea, .stTextInput input {
    background-color: #FFFFFF !important;
    border: 1px solid #D5E0D9 !important;
    border-radius: 8px !important;
    color: #0F172A !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
    line-height: 1.6 !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #065F46 !important;
    box-shadow: 0 0 0 1px rgba(6, 95, 70, 0.2) !important;
}
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #D5E0D9 !important;
    border-radius: 8px !important;
    color: #0F172A !important;
}

/* File Uploader */
section[data-testid="stFileUploaderDropzone"] {
    background-color: #FFFFFF !important;
    border: 1px dashed #B8C9BF !important;
    border-radius: 10px !important;
}
section[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #065F46 !important;
}

/* Metric Boxes */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #D8E3DC;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(6, 78, 59, 0.03);
}
div[data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 24px !important;
}

/* Pure White Floating Editorial Cards */
.editorial-card {
    background-color: #FFFFFF;
    border: 1px solid #D8E3DC;
    border-radius: 14px;
    padding: 20px 22px;
    height: 100%;
    box-shadow: 0 2px 10px rgba(6, 78, 59, 0.04);
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #E8EFEA;
}
.card-title {
    font-size: 14.5px;
    font-weight: 700;
    color: #0F172A;
}
.score-pill {
    font-family: 'JetBrains Mono', monospace;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11.5px;
    font-weight: 600;
}
.pill-blue { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.pill-amber { background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.pill-red { background-color: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
.pill-green { background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }

.section-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748B;
    margin-top: 14px;
    margin-bottom: 6px;
}
.tag-chip {
    display: inline-block;
    background-color: #F8FAF9;
    border: 1px solid #D8E3DC;
    color: #334155;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    margin: 3px 5px 3px 0;
    line-height: 1.5;
}
.tag-chip.warn {
    background-color: #FEF2F2;
    border-color: #FECACA;
    color: #991B1B;
}
.tag-chip.mono {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: #065F46;
    background-color: #ECFDF5;
    border-color: #A7F3D0;
}

/* Verdict Banner */
.verdict-banner {
    border-radius: 14px;
    padding: 22px 26px;
    border: 1px solid #D8E3DC;
    box-shadow: 0 2px 10px rgba(6, 78, 59, 0.04);
    height: 100%;
}
.verdict-buy {
    background-color: #ECFDF5;
    border-color: #A7F3D0;
}
.verdict-pass {
    background-color: #FEF2F2;
    border-color: #FECACA;
}
.gate-pill {
    display: inline-block;
    background-color: #ECFDF5;
    border: 1px solid #A7F3D0;
    color: #065F46;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 999px;
    letter-spacing: 0.06em;
    margin-bottom: 14px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# Access Gate: Poe API Key Submission
# ==========================================
if "poe_api_key" not in st.session_state:
    st.session_state.poe_api_key = ""

if not st.session_state.poe_api_key:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        st.markdown(
            """
<div style="text-align:center; margin-bottom:28px;">
<div class="gate-pill">MULTI-AGENT TRANSFER COMMITTEE</div>
<h1 style="margin:0; font-size:34px; color:#0F172A;">Pixel Scouting HQ</h1>
<p style="color:#475569; margin-top:10px; font-size:15px;">
U21 football transfer analytics powered by 4 heterogeneous AI scouts via Poe API.
</p>
</div>
""",
            unsafe_allow_html=True,
        )
        with st.form("api_key_gate"):
            st.markdown("#### Enter Poe API Key")
            st.caption(
                "Stored strictly in your active browser session. Obtain your key at [poe.com/api/keys](https://poe.com/api/keys)."
            )
            input_key = st.text_input(
                "Poe API Key",
                type="password",
                placeholder="Paste your Poe API Key...",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Enter Pitch Studio →", type="primary", use_container_width=True)
            if submitted:
                cleaned = input_key.strip()
                if not cleaned:
                    st.error("Please enter a valid Poe API Key.")
                else:
                    st.session_state.poe_api_key = cleaned
                    st.rerun()
    st.stop()


# ==========================================
# Constants: Frontier Models, Agents & Samples
# ==========================================
POE_MODEL_OPTIONS = [
    "GPT-5.4",
    "GPT-5.4-mini",
    "Claude-Opus-4.6",
    "Claude-Sonnet-4.6",
    "Gemini-3.1-Pro",
    "o3-pro",
    "o3",
    "Grok-4",
    "DeepSeek-R1",
    "Custom Bot Name...",
]

CANARY_AUDIT_PROMPT = (
    "You are a football historian and anti-leakage auditor. Examine the provided player profile. "
    "Determine whether you can reliably identify who this real-world footballer is based ONLY on this data. "
    "Return strict JSON in English: "
    '{"can_identify": true or false, "confidence": "High" or "Medium" or "Low", '
    '"top3_guesses": ["Name 1", "Name 2", "Name 3"], "reason": "concise 1-sentence explanation"}'
)

AGENT_SPECS = {
    "tech_scout": {
        "name": "Tech Scout",
        "tag": "AGENT 01",
        "default_model": "GPT-5.4-mini",
        "color": "#2563EB",
        "prompt": (
            "You are a professional football data scout. Based strictly on the anonymized profile, evaluate "
            "the player's 3-5 year sporting upside from age curve, minutes stability, and per-90 output. "
            "Never guess the player's real name. Return strict JSON in English: "
            '{"tech_score": 1-10, "strengths": ["..."], "weaknesses": ["..."], "summary": "concise 1-sentence summary"}'
        ),
    },
    "valuation_analyst": {
        "name": "Valuation Analyst",
        "tag": "AGENT 02",
        "default_model": "Claude-Sonnet-4.6",
        "color": "#D97706",
        "prompt": (
            "You are a football transfer market economist focused on Buy-Low, Sell-High arbitrage. "
            "Assess valuation percentile, stepping-stone league premium, and 5-year 3x ROI risk/reward. "
            "Return strict JSON in English: "
            '{"value_score": 1-10, "fair_multiple_5y": 2.5, "upside_case": "...", "summary": "concise 1-sentence summary"}'
        ),
    },
    "risk_skeptic": {
        "name": "Risk Skeptic",
        "tag": "AGENT 03",
        "default_model": "Gemini-3.1-Pro",
        "color": "#DC2626",
        "prompt": (
            "You are the Transfer Risk Skeptic (Devil's Advocate). Your sole job is to expose why this player "
            "could become a bust: small sample size, weak-league stat padding, physical/injury flags, or valuation traps. "
            "Return strict JSON in English: "
            '{"bust_risk_score": 1-10, "red_flags": ["..."], "summary": "concise 1-sentence summary"}'
        ),
    },
    "chief_scout": {
        "name": "Chief Chair",
        "tag": "AGENT 04",
        "default_model": "GPT-5.4",
        "color": "#059669",
        "prompt": (
            "You are the Chief Scout & Transfer Investment Chair. Synthesize all three specialist reports, weighing "
            "sporting upside, valuation odds, and red flags. Issue BUY only if 5-year value appreciation >= 3x is "
            "realistic with controlled downside (target top 30%-40% selectivity); otherwise PASS. "
            'Return strict JSON in English: {"decision": "BUY" or "PASS", "investment_score": 1-100, "key_reason": "concise verdict rationale"}'
        ),
    },
}

SAMPLE_PLAYERS = {
    "Player_P07 — High-Upside Winger (Anonymized)": {
        "player_id": "Player_P07",
        "age": 19.3,
        "position": "Winger / Attacking Midfielder",
        "league_tier": "Tier-2 European Developmental League (Upper-Mid Table)",
        "region": "Western Europe",
        "minutes_played": 1840,
        "valuation_percentile_u21": "68th percentile (0.92x league median)",
        "goals_per_90": 0.49,
        "assists_per_90": 0.21,
        "key_attributes": {"pace": 83, "dribbling": 80, "passing": 73, "physical": 61, "stamina": 74},
    },
    "Player_P14 — Stat-Padding Striker (Risk Trap)": {
        "player_id": "Player_P14",
        "age": 20.4,
        "position": "Center Forward",
        "league_tier": "Tier-3 European League (Title Contender)",
        "region": "Northern Europe",
        "minutes_played": 780,
        "valuation_percentile_u21": "81st percentile (1.45x league median)",
        "goals_per_90": 0.68,
        "assists_per_90": 0.05,
        "key_attributes": {"pace": 71, "dribbling": 64, "passing": 58, "physical": 79, "stamina": 62},
    },
    "Raw Sample — Unmasked Player (Test Auto-Anonymize)": {
        "name": "Sample Prospect",
        "club": "Ajax Amsterdam",
        "league": "Eredivisie",
        "nationality": "Netherlands",
        "season": "2015/16",
        "potential": 86,
        "age": 19.2,
        "position": "Central Midfielder",
        "minutes_played": 1620,
        "goals_per_90": 0.28,
        "assists_per_90": 0.34,
        "key_attributes": {"pace": 76, "dribbling": 82, "passing": 81, "physical": 66, "stamina": 79},
    },
}


# ==========================================
# Helper: Zero-Dependency Markdown Table Builder
# ==========================================
def df_to_md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        vals = [str(v).replace("|", "\\|").replace("\n", " ") for v in row.values]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep] + rows)


# ==========================================
# L2 + L3 Built-in Auto-Anonymizer Engine
# ==========================================
SENSITIVE_KEYS = {
    "name", "player_name", "full_name", "club", "team", "club_name",
    "league", "league_name", "nationality", "country", "dob", "birth_date",
    "season", "year", "potential", "market_value_eur",
}

def anonymize_profile(raw: dict) -> tuple[dict, list[str]]:
    removed = []
    cleaned = {}
    pid = raw.get("player_id") or f"Player_Anon_{random.randint(100, 999)}"
    cleaned["player_id"] = str(pid)

    for k, v in raw.items():
        if k == "player_id":
            continue
        if k.lower() in SENSITIVE_KEYS:
            removed.append(k)
            continue

        if k.lower() == "age" and isinstance(v, (int, float)):
            cleaned[k] = round(float(v), 1)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            new_val = v * random.uniform(0.96, 1.04)
            cleaned[k] = int(round(new_val)) if isinstance(v, int) else round(new_val, 2)
        elif isinstance(v, dict):
            sub_dict = {}
            for sk, sv in v.items():
                if sk.lower() in SENSITIVE_KEYS:
                    removed.append(f"{k}.{sk}")
                    continue
                if isinstance(sv, (int, float)) and not isinstance(sv, bool):
                    nv = sv * random.uniform(0.96, 1.04)
                    sub_dict[sk] = int(round(nv)) if isinstance(sv, int) else round(nv, 2)
                else:
                    sub_dict[sk] = sv
            cleaned[k] = sub_dict
        else:
            cleaned[k] = v

    if "league_tier" not in cleaned:
        cleaned["league_tier"] = "Tier-2 European Developmental League (Masked)"
    cleaned["anonymization_status"] = "L2_Masked + L3_Perturbed(±4%)"
    return cleaned, removed


def handle_auto_anonymize(state_key: str):
    """Callback safe for modifying widget session state before re-render."""
    try:
        raw_prof = json.loads(st.session_state[state_key])
        anon_prof, removed_fields = anonymize_profile(raw_prof)
        st.session_state[state_key] = json.dumps(anon_prof, ensure_ascii=False, indent=2)
        msg = f"Stripped: {', '.join(removed_fields)}" if removed_fields else "Applied ±4% L3 noise."
        st.toast(f"Anonymized. {msg}")
    except Exception as e:
        st.toast(f"Invalid JSON: {e}")


# ==========================================
# Poe API Client (Hardened JSON & Anti-Search)
# ==========================================
def get_poe_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url="https://api.poe.com/v1")


def call_poe_json(client: OpenAI, model: str, system_prompt: str, user_content: str, retries: int = 2) -> dict:
    strict_system = (
        system_prompt
        + "\n\nCRITICAL RULES: Do NOT search the web, do NOT invoke any tools, and do NOT write any "
        "introductory text or plans. Output ONLY a single valid JSON object starting with '{' and ending with '}'."
    )
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=0.2,
                max_tokens=2048,
                messages=[
                    {"role": "system", "content": strict_system},
                    {"role": "user", "content": user_content},
                ],
            )
            raw = resp.choices[0].message.content or ""
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                return json.loads(match.group(0))
            if attempt == retries:
                return {"raw": raw, "parse_warning": "Non-JSON response"}
            time.sleep(1.5 * (attempt + 1))
        except Exception as e:
            time.sleep(1.5 * (attempt + 1))
            if attempt == retries:
                return {"error": str(e)}
    return {"error": "Unknown error"}


def run_4agent_canary(client: OpenAI, active_models: dict, profile_str: str) -> dict:
    role_keys = ["tech_scout", "valuation_analyst", "risk_skeptic", "chief_scout"]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {
            r: ex.submit(call_poe_json, client, active_models[r], CANARY_AUDIT_PROMPT, profile_str)
            for r in role_keys
        }
        return {r: f.result() for r, f in futures.items()}


# ==========================================
# 5-Axis Radar Chart (Compact Single-Line SVG) & Report Generators
# ==========================================
def _safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def build_radar_svg(reports: dict, final: dict) -> str:
    tech = min(10.0, max(0.0, _safe_float(reports.get("tech", {}).get("tech_score"), 5.0)))
    val = min(10.0, max(0.0, _safe_float(reports.get("valuation", {}).get("value_score"), 5.0)))
    bust = min(10.0, max(0.0, _safe_float(reports.get("risk", {}).get("bust_risk_score"), 5.0)))
    safety = round(max(0.0, 10.0 - bust), 1)
    conv = round(min(10.0, max(0.0, _safe_float(final.get("investment_score"), 50.0) / 10.0)), 1)
    mult_raw = _safe_float(reports.get("valuation", {}).get("fair_multiple_5y"), 2.0)
    roi_pot = round(min(10.0, max(0.0, mult_raw * 2.0)), 1)

    axes = [
        ("Tech Upside", tech),
        ("Valuation", val),
        ("Risk Safety", safety),
        ("Conviction", conv),
        ("5Y ROI Mult", roi_pot),
    ]

    cx, cy, max_r = 160, 128, 74
    angles = [-math.pi / 2 + i * (2 * math.pi / 5) for i in range(5)]

    parts = ['<svg viewBox="0 0 320 250" width="100%" height="235" xmlns="http://www.w3.org/2000/svg">']
    for frac in [0.2, 0.4, 0.6, 0.8, 1.0]:
        pts = " ".join(f"{cx + max_r * frac * math.cos(a):.1f},{cy + max_r * frac * math.sin(a):.1f}" for a in angles)
        parts.append(f'<polygon points="{pts}" fill="none" stroke="#DCE7E0" stroke-width="1"/>')

    data_pts = []
    dots = []
    labels = []
    for (label, score), a in zip(axes, angles):
        x2 = cx + max_r * math.cos(a)
        y2 = cy + max_r * math.sin(a)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#DCE7E0" stroke-width="1"/>')

        r = max_r * (score / 10.0)
        px = cx + r * math.cos(a)
        py = cy + r * math.sin(a)
        data_pts.append(f"{px:.1f},{py:.1f}")
        dots.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#065F46" stroke="#FFFFFF" stroke-width="1.5"/>')

        lx = cx + (max_r + 24) * math.cos(a)
        ly = cy + (max_r + 19) * math.sin(a)
        anchor = "middle"
        if math.cos(a) > 0.25:
            anchor = "start"
            lx -= 4
        elif math.cos(a) < -0.25:
            anchor = "end"
            lx += 4
        labels.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
            f'font-family="Inter, sans-serif" font-size="10.5" font-weight="600" fill="#334155">{label}</text>'
            f'<text x="{lx:.1f}" y="{ly + 12:.1f}" text-anchor="{anchor}" '
            f'font-family="JetBrains Mono, monospace" font-size="10" font-weight="600" fill="#065F46">{score:.1f}/10</text>'
        )

    parts.append(f'<polygon points="{" ".join(data_pts)}" fill="rgba(6, 95, 70, 0.16)" stroke="#065F46" stroke-width="2"/>')
    parts.extend(dots)
    parts.extend(labels)
    parts.append("</svg>")
    return "".join(parts)


def build_scouting_report_md(pid: str, profile: dict, reports: dict, final: dict, models: dict) -> str:
    t, v, r = reports.get("tech", {}), reports.get("valuation", {}), reports.get("risk", {})
    fence = "`" * 3
    return f"""# Football Scouting & Transfer Investment Dossier — {pid}

**Verdict:** `{str(final.get('decision', 'PASS')).upper()}` | **Investment Score:** `{final.get('investment_score', '?')} / 100`

## 1. Executive Verdict (Agent 4: Chief Chair · `{models.get('chief_scout', '')}`)
> {final.get('key_reason', 'N/A')}

## 2. 5-Dimensional Scorecard
| Dimension | Score | Basis |
| :--- | :---: | :--- |
| Tech Upside | {t.get('tech_score', '?')} / 10 | Agent 1 ({models.get('tech_scout', '')}) |
| Market Valuation | {v.get('value_score', '?')} / 10 | Agent 2 ({models.get('valuation_analyst', '')}) |
| Bust Risk | {r.get('bust_risk_score', '?')} / 10 | Agent 3 ({models.get('risk_skeptic', '')}) |
| 5-Year Fair Multiple | {v.get('fair_multiple_5y', '?')}x | Valuation Analyst |
| Committee Conviction | {final.get('investment_score', '?')} / 100 | Chief Investment Chair |

## 3. Specialist Breakdown
### Tech Scout
- **Summary:** {t.get('summary', 'N/A')}
- **Strengths:** {', '.join(t.get('strengths', [])) if isinstance(t.get('strengths'), list) else 'None'}
- **Weaknesses:** {', '.join(t.get('weaknesses', [])) if isinstance(t.get('weaknesses'), list) else 'None'}

### Valuation Analyst
- **Summary:** {v.get('summary', 'N/A')}
- **Upside Case:** {v.get('upside_case', 'N/A')}

### Risk Skeptic (Devil's Advocate)
- **Summary:** {r.get('summary', 'N/A')}
- **Red Flags:** {', '.join(r.get('red_flags', [])) if isinstance(r.get('red_flags'), list) else 'None'}

## 4. Anonymized Input Profile
{fence}json
{json.dumps(profile, ensure_ascii=False, indent=2)}
{fence}
"""


def build_scouting_report_html(pid: str, reports: dict, final: dict, radar_svg: str, models: dict) -> str:
    t, v, r = reports.get("tech", {}), reports.get("valuation", {}), reports.get("risk", {})
    dec = str(final.get("decision", "PASS")).upper()
    badge_bg = "#065F46" if dec == "BUY" else "#991B1B"

    def li_list(items):
        if not items or not isinstance(items, list):
            return "<li>None</li>"
        return "".join(f"<li>{html.escape(str(x))}</li>" for x in items)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Scouting Report — {html.escape(pid)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif; background:#F3F6F4; color:#0F172A; margin:0; padding:36px; line-height:1.65; }}
  .sheet {{ max-width:860px; margin:0 auto; background:#FFFFFF; border:1px solid #D8E3DC; border-radius:16px; padding:36px 40px; }}
  .top {{ display:flex; justify-content:space-between; align-items:flex-start; border-bottom:1px solid #E8EFEA; padding-bottom:20px; }}
  .badge {{ background:{badge_bg}; color:#FFF; padding:5px 14px; border-radius:6px; font-weight:700; font-size:15px; display:inline-block; }}
  .grid-2 {{ display:grid; grid-template-columns:1.2fr 1fr; gap:24px; margin-top:24px; align-items:center; }}
  .card {{ background:#FAFDFB; border:1px solid #DCE7E0; border-radius:12px; padding:18px 20px; margin-top:16px; }}
  h1 {{ margin:0; font-size:26px; }} h2 {{ font-size:16px; margin:0 0 8px 0; color:#065F46; }}
  ul {{ margin:6px 0 0 18px; padding:0; }}
</style>
</head>
<body>
  <div class="sheet">
    <div class="top">
      <div>
        <div style="font-size:11px; letter-spacing:0.08em; color:#64748B; font-weight:700;">PIXEL SCOUTING HQ · TRANSFER COMMITTEE REPORT</div>
        <h1>{html.escape(pid)}</h1>
      </div>
      <div style="text-align:right;">
        <span class="badge">{html.escape(dec)}</span>
        <div style="font-size:14px; font-weight:700; margin-top:6px;">Score: {html.escape(str(final.get('investment_score', '?')))} / 100</div>
      </div>
    </div>
    <div class="grid-2">
      <div>
        <h2>Executive Verdict ({html.escape(models.get('chief_scout', ''))})</h2>
        <p>{html.escape(str(final.get('key_reason', 'N/A')))}</p>
      </div>
      <div>{radar_svg}</div>
    </div>
    <div class="card">
      <h2>1. Tech Scout — {html.escape(str(t.get('tech_score', '?')))} / 10 ({html.escape(models.get('tech_scout', ''))})</h2>
      <p>{html.escape(str(t.get('summary', 'N/A')))}</p>
      <strong>Strengths:</strong><ul>{li_list(t.get('strengths'))}</ul>
      <strong>Weaknesses:</strong><ul>{li_list(t.get('weaknesses'))}</ul>
    </div>
    <div class="card">
      <h2>2. Valuation Analyst — {html.escape(str(v.get('value_score', '?')))} / 10 · {html.escape(str(v.get('fair_multiple_5y', '?')))}x ({html.escape(models.get('valuation_analyst', ''))})</h2>
      <p>{html.escape(str(v.get('summary', 'N/A')))}</p>
      <p><strong>Upside Case:</strong> {html.escape(str(v.get('upside_case', 'N/A')))}</p>
    </div>
    <div class="card">
      <h2>3. Risk Skeptic — Bust Risk {html.escape(str(r.get('bust_risk_score', '?')))} / 10 ({html.escape(models.get('risk_skeptic', ''))})</h2>
      <p>{html.escape(str(r.get('summary', 'N/A')))}</p>
      <strong>Red Flags:</strong><ul>{li_list(r.get('red_flags'))}</ul>
    </div>
  </div>
</body>
</html>"""


# ==========================================
# Subtle Pitch-Themed Pixel Studio (HTML/SVG)
# ==========================================
def render_pixel_office(agent_states: dict, active_models: dict, current_player: str = "Standby"):
    def pixel_avatar_svg(role_key: str, shirt_color: str, is_working: bool) -> str:
        anim_class = "typing-bounce" if is_working else ""
        screen_color = "#10B981" if is_working else "#94A3B8"

        accessory = ""
        if role_key == "tech_scout":
            accessory = '<rect x="5" y="5" width="3" height="1" fill="#1D4ED8"/><rect x="10" y="5" width="3" height="1" fill="#1D4ED8"/><rect x="8" y="5" width="2" height="1" fill="#64748B"/>'
        elif role_key == "risk_skeptic":
            accessory = '<rect x="3" y="4" width="1" height="3" fill="#DC2626"/><rect x="14" y="4" width="1" height="3" fill="#DC2626"/>'
        elif role_key == "chief_scout":
            accessory = '<rect x="8" y="9" width="2" height="3" fill="#F59E0B"/>'

        return (
            f'<svg class="pixel-sprite {anim_class}" viewBox="0 0 18 16" width="76" height="68" xmlns="http://www.w3.org/2000/svg">'
            '<rect x="5" y="1" width="8" height="2" fill="#334155"/>'
            '<rect x="4" y="2" width="1" height="2" fill="#334155"/>'
            '<rect x="13" y="2" width="1" height="2" fill="#334155"/>'
            '<rect x="5" y="3" width="8" height="5" fill="#F3CFA2"/>'
            '<rect x="6" y="5" width="2" height="1" fill="#0F172A"/>'
            '<rect x="10" y="5" width="2" height="1" fill="#0F172A"/>'
            f'{accessory}'
            f'<rect x="4" y="8" width="10" height="5" fill="{shirt_color}"/>'
            '<rect x="8" y="8" width="2" height="2" fill="#FFFFFF"/>'
            '<rect x="1" y="13" width="16" height="3" fill="#D6B892"/>'
            '<rect x="1" y="13" width="16" height="1" fill="#E5CEAF"/>'
            '<rect x="2" y="11" width="2" height="2" fill="#E2E8F0"/>'
            '<rect x="6" y="10" width="6" height="3" fill="#334155"/>'
            f'<rect x="7" y="11" width="4" height="1" fill="{screen_color}"/>'
            '<rect x="14" y="11" width="2" height="2" fill="#B45309"/>'
            '<rect x="14" y="9" width="2" height="2" fill="#10B981"/>'
            '</svg>'
        )

    safe_player = html.escape(str(current_player))
    cards_html = ""
    for role_key in ["tech_scout", "valuation_analyst", "risk_skeptic", "chief_scout"]:
        cfg = AGENT_SPECS[role_key]
        model_name = html.escape(str(active_models.get(role_key, cfg["default_model"])))
        st_info = agent_states.get(role_key, {"status": "IDLE", "bubble": "Awaiting profile...", "badge": ""})
        status = st_info["status"]
        bubble = html.escape(str(st_info["bubble"])).replace("\n", "<br>")
        badge = st_info.get("badge", "")

        status_color = {"IDLE": "#94A3B8", "WORKING": "#D97706", "DONE": "#059669", "ERROR": "#DC2626"}.get(status, "#94A3B8")
        badge_html = ""
        if badge == "BUY":
            badge_html = '<span class="decision-badge buy">BUY</span>'
        elif badge == "PASS":
            badge_html = '<span class="decision-badge pass">PASS</span>'
        elif badge == "SAFE":
            badge_html = '<span class="decision-badge buy">SAFE · UNKNOWN</span>'
        elif badge == "LEAK?":
            badge_html = '<span class="decision-badge pass">LEAK? · IDENTIFIED</span>'

        cards_html += f"""
        <div class="desk-card {'working-border' if status == 'WORKING' else ''}">
            <div class="speech-bubble">
                {badge_html}
                <div class="bubble-text">{bubble}</div>
            </div>
            <div class="avatar-wrap">{pixel_avatar_svg(role_key, cfg['color'], status == 'WORKING')}</div>
            <div class="role-tag">{cfg['tag']}</div>
            <div class="agent-name">{html.escape(cfg['name'])}</div>
            <div class="agent-meta">
                <span class="status-dot" style="background:{status_color};"></span>
                <span>{html.escape(status)}</span> · <span class="model-tag">{model_name}</span>
            </div>
        </div>
        """

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');
        body {{ margin: 0; padding: 2px; background: transparent; font-family: 'Inter', sans-serif; }}
        .office-floor {{
            background-color: #FFFFFF;
            background-image: radial-gradient(#C8D8CE 1px, transparent 1px);
            background-size: 20px 20px;
            border: 1px solid #D8E3DC;
            border-radius: 16px;
            padding: 20px 22px 24px 22px;
            color: #0F172A;
            box-shadow: 0 2px 12px rgba(6, 78, 59, 0.04);
        }}
        .office-header {{
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 20px; border-bottom: 1px solid #E8EFEA; padding-bottom: 12px;
        }}
        .studio-title {{
            font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600;
            color: #065F46; letter-spacing: 0.06em;
        }}
        .target-tag {{
            background-color: #ECFDF5; border: 1px solid #A7F3D0;
            padding: 4px 12px; border-radius: 999px; font-size: 11.5px; font-weight: 600;
            color: #065F46; font-family: 'JetBrains Mono', monospace;
        }}
        .desks-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
        .desk-card {{
            background-color: #FAFDFB; border: 1px solid #DCE7E0;
            border-radius: 12px; padding: 16px 12px; display: flex; flex-direction: column;
            align-items: center; transition: border-color 0.2s ease;
        }}
        .working-border {{
            border-color: #059669;
            background-color: #F0FDF4;
        }}
        .speech-bubble {{
            background-color: #FFFFFF; color: #0F172A; border: 1px solid #D8E3DC;
            border-radius: 8px; padding: 8px 10px; font-size: 12px; line-height: 1.45;
            width: 92%; min-height: 44px; margin-bottom: 12px; position: relative;
            text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;
        }}
        .speech-bubble::after {{
            content: ''; position: absolute; bottom: -6px; left: 50%; transform: translateX(-50%);
            border-width: 6px 6px 0; border-style: solid; border-color: #FFFFFF transparent transparent transparent;
        }}
        .bubble-text {{ word-break: break-word; font-weight: 500; }}
        .decision-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; margin-bottom: 4px; letter-spacing: 0.05em; }}
        .decision-badge.buy {{ background-color: #DCFCE7; color: #166534; }}
        .decision-badge.pass {{ background-color: #FEE2E2; color: #991B1B; }}
        .pixel-sprite {{ image-rendering: pixelated; margin: 2px 0 6px 0; }}
        @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
        .typing-bounce {{ animation: bounce 0.45s infinite; }}
        .role-tag {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #64748B; letter-spacing: 0.06em; }}
        .agent-name {{ font-weight: 700; font-size: 13.5px; margin-top: 2px; color: #0F172A; }}
        .agent-meta {{ font-size: 11px; color: #64748B; margin-top: 4px; display: flex; align-items: center; gap: 5px; }}
        .status-dot {{ width: 7px; height: 7px; border-radius: 50%; display: inline-block; }}
        .model-tag {{ color: #475569; font-family: 'JetBrains Mono', monospace; font-size: 10.5px; }}
    </style>
    </head>
    <body>
        <div class="office-floor">
            <div class="office-header">
                <div class="studio-title">PITCH SCOUTING STUDIO // 4-AGENT COMMITTEE</div>
                <div class="target-tag">TARGET: {safe_player}</div>
            </div>
            <div class="desks-grid">{cards_html}</div>
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=345)


def render_tags(items, css_class=""):
    if not items or not isinstance(items, list):
        return "<span style='color:#94A3B8;font-size:12px;'>None</span>"
    return "".join([f'<span class="tag-chip {css_class}">{html.escape(str(i))}</span>' for i in items])


def render_4agent_canary_cards(canary_results: dict, active_models: dict):
    st.markdown("### 4-Agent Pre-Check: Identity Leakage Audit")
    cols = st.columns(4, gap="medium")
    for col, role_key in zip(cols, ["tech_scout", "valuation_analyst", "risk_skeptic", "chief_scout"]):
        res = canary_results.get(role_key, {})
        cfg = AGENT_SPECS[role_key]
        can_id = bool(res.get("can_identify", False))
        pill_cls = "pill-red" if can_id else "pill-green"
        pill_txt = "CAN IDENTIFY" if can_id else "UNKNOWN"
        conf = html.escape(str(res.get("confidence", "Low")))
        reason = html.escape(str(res.get("reason", res.get("error", "No explanation."))))
        guesses = res.get("top3_guesses", [])

        with col:
            st.markdown(
                f'<div class="editorial-card">'
                f'<div class="card-header"><span class="card-title">{html.escape(cfg["name"])}</span>'
                f'<span class="score-pill {pill_cls}">{pill_txt}</span></div>'
                f'<div style="font-size:11px; color:#64748B; font-family:\'JetBrains Mono\',monospace;">'
                f'{html.escape(active_models[role_key])} · Conf: {conf}</div>'
                f'<div class="section-label">Top-3 Blind Guesses</div>'
                f'<div>{render_tags(guesses, "warn" if can_id else "")}</div>'
                f'<div class="section-label">Audit Rationale</div>'
                f'<p style="font-size:12.5px; color:#334155; margin:0;">{reason}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ==========================================
# Minimalist Sidebar Controls
# ==========================================
poe_api_key = st.session_state.poe_api_key
active_models = {}

with st.sidebar:
    st.markdown("### Workspace")
    mode = st.radio(
        "Navigation",
        [
            "1. Single-Player Scouting",
            "2. L4 Canary Audit (4-Agent)",
            "3. Batch Backtest",
            "4. Backtest Evaluation",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    with st.expander("Model Routing (Poe Bots)", expanded=False):
        for role_key, cfg in AGENT_SPECS.items():
            default_idx = POE_MODEL_OPTIONS.index(cfg["default_model"]) if cfg["default_model"] in POE_MODEL_OPTIONS else 0
            selected = st.selectbox(
                cfg["name"],
                options=POE_MODEL_OPTIONS,
                index=default_idx,
                format_func=lambda m, rec=cfg["default_model"]: f"🌟 {m}" if m == rec else m,
                key=f"select_{role_key}",
            )
            if selected == "Custom Bot Name...":
                custom_val = st.text_input(
                    f"Custom Bot ({cfg['name']})",
                    value=cfg["default_model"],
                    key=f"custom_{role_key}",
                ).strip()
                active_models[role_key] = custom_val or cfg["default_model"]
            else:
                active_models[role_key] = selected

    st.divider()
    st.caption("Poe API Connected (Session Only)")
    if st.button("Disconnect / Switch Key", use_container_width=True):
        st.session_state.poe_api_key = ""
        st.rerun()

# ==========================================
# Main Header & Pixel Studio
# ==========================================
st.markdown("## Pixel Scouting HQ")
st.caption("4-Agent Transfer Investment Committee · Offline L1 Poe API · 5D Radar Dossier & Ground Truth Comparator")

office_placeholder = st.empty()

if "agent_states" not in st.session_state:
    st.session_state.agent_states = {
        k: {"status": "IDLE", "bubble": "Awaiting profile...", "badge": ""}
        for k in AGENT_SPECS.keys()
    }
if "current_player_id" not in st.session_state:
    st.session_state.current_player_id = "Standby"

with office_placeholder:
    render_pixel_office(st.session_state.agent_states, active_models, st.session_state.current_player_id)

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# ==========================================
# Mode 1: Single-Player Blind Scouting + 5D Radar + One-Click Report
# ==========================================
if mode == "1. Single-Player Scouting":
    if "profile_editor" not in st.session_state:
        first_key = list(SAMPLE_PLAYERS.keys())[0]
        st.session_state.profile_editor = json.dumps(SAMPLE_PLAYERS[first_key], ensure_ascii=False, indent=2)
        st.session_state.last_sample = first_key

    col_input, col_action = st.columns([2.2, 1], gap="large")

    with col_input:
        c_up, c_sel = st.columns(2, gap="medium")
        with c_up:
            uploaded_single = st.file_uploader("Upload Profile (.json)", type=["json"], key="single_upload")
            if uploaded_single is not None:
                try:
                    loaded_obj = json.load(uploaded_single)
                    if isinstance(loaded_obj, list) and len(loaded_obj) > 0:
                        loaded_obj = loaded_obj[0]
                    st.session_state.profile_editor = json.dumps(loaded_obj, ensure_ascii=False, indent=2)
                except Exception as e:
                    st.error(f"Failed to parse JSON: {e}")

        with c_sel:
            sample_choice = st.selectbox("Preset Sample", list(SAMPLE_PLAYERS.keys()))
            if sample_choice != st.session_state.last_sample:
                st.session_state.last_sample = sample_choice
                st.session_state.profile_editor = json.dumps(SAMPLE_PLAYERS[sample_choice], ensure_ascii=False, indent=2)

        profile_text = st.text_area("Player Profile (JSON)", key="profile_editor", height=230)

    with col_action:
        st.markdown(
            '<div class="editorial-card" style="margin-top:4px;">'
            '<div style="font-weight:700; color:#065F46; font-size:13.5px; margin-bottom:10px;">Workflow</div>'
            '<p style="font-size:13px; color:#475569; margin:0;">'
            '<b>1. Mask:</b> Strip identities &amp; add ±4% noise.<br>'
            '<b>2. Pre-Check:</b> Ask all 4 judges if they recognize the player.<br>'
            '<b>3. Evaluate:</b> Generate verdict, 5D radar &amp; downloadable report.'
            '</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        st.button(
            "1. Auto-Anonymize (L2 + L3)",
            on_click=handle_auto_anonymize,
            args=("profile_editor",),
            use_container_width=True,
        )

        canary_pre_btn = st.button("2. Pre-Check: 4-Agent Canary", use_container_width=True)
        run_btn = st.button("3. Run 4-Agent Evaluation", type="primary", use_container_width=True)

    if canary_pre_btn:
        try:
            profile = json.loads(profile_text)
        except json.JSONDecodeError as e:
            st.error(f"JSON Syntax Error: {e}")
            st.stop()

        client = get_poe_client(poe_api_key)
        pid = str(profile.get("player_id", "Unknown_Player"))
        st.session_state.current_player_id = f"{pid} (Canary)"
        p_str = json.dumps(profile, ensure_ascii=False, indent=2)

        for r in AGENT_SPECS.keys():
            st.session_state.agent_states[r] = {"status": "WORKING", "bubble": "Checking identity...", "badge": ""}
        with office_placeholder:
            render_pixel_office(st.session_state.agent_states, active_models, st.session_state.current_player_id)

        canary_res = run_4agent_canary(client, active_models, p_str)

        for r, rep in canary_res.items():
            if "error" in rep:
                st.session_state.agent_states[r] = {"status": "ERROR", "bubble": str(rep["error"])[:36], "badge": ""}
            else:
                can_id = bool(rep.get("can_identify", False))
                conf = rep.get("confidence", "Low")
                top1 = rep.get("top3_guesses", ["None"])[0] if isinstance(rep.get("top3_guesses"), list) and rep.get("top3_guesses") else "None"
                st.session_state.agent_states[r] = {
                    "status": "DONE",
                    "bubble": f"Guess: {top1}\nConf: {conf}",
                    "badge": "LEAK?" if can_id else "SAFE",
                }
        with office_placeholder:
            render_pixel_office(st.session_state.agent_states, active_models, st.session_state.current_player_id)

        st.divider()
        render_4agent_canary_cards(canary_res, active_models)

    if run_btn:
        try:
            profile = json.loads(profile_text)
        except json.JSONDecodeError as e:
            st.error(f"JSON Syntax Error: {e}")
            st.stop()

        client = get_poe_client(poe_api_key)
        pid = str(profile.get("player_id", "Unknown_Player"))
        st.session_state.current_player_id = pid
        p_str = json.dumps(profile, ensure_ascii=False, indent=2)

        for r in ["tech_scout", "valuation_analyst", "risk_skeptic"]:
            st.session_state.agent_states[r] = {"status": "WORKING", "bubble": "Analyzing metrics...", "badge": ""}
        st.session_state.agent_states["chief_scout"] = {"status": "IDLE", "bubble": "Awaiting reports...", "badge": ""}
        with office_placeholder:
            render_pixel_office(st.session_state.agent_states, active_models, pid)

        with ThreadPoolExecutor(max_workers=3) as ex:
            f1 = ex.submit(call_poe_json, client, active_models["tech_scout"], AGENT_SPECS["tech_scout"]["prompt"], p_str)
            f2 = ex.submit(call_poe_json, client, active_models["valuation_analyst"], AGENT_SPECS["valuation_analyst"]["prompt"], p_str)
            f3 = ex.submit(call_poe_json, client, active_models["risk_skeptic"], AGENT_SPECS["risk_skeptic"]["prompt"], p_str)
            reports = {"tech": f1.result(), "valuation": f2.result(), "risk": f3.result()}

        def update_stage1(role_key, rep, score_field, label):
            if "error" in rep:
                st.session_state.agent_states[role_key] = {"status": "ERROR", "bubble": str(rep["error"])[:38], "badge": ""}
            else:
                sc = rep.get(score_field, "?")
                summ = str(rep.get("summary", "Complete"))[:26]
                st.session_state.agent_states[role_key] = {"status": "DONE", "bubble": f"{label}: {sc}/10\n{summ}...", "badge": ""}

        update_stage1("tech_scout", reports["tech"], "tech_score", "Tech")
        update_stage1("valuation_analyst", reports["valuation"], "value_score", "Value")
        update_stage1("risk_skeptic", reports["risk"], "bust_risk_score", "Risk")

        st.session_state.agent_states["chief_scout"] = {"status": "WORKING", "bubble": "Synthesizing...", "badge": ""}
        with office_placeholder:
            render_pixel_office(st.session_state.agent_states, active_models, pid)

        chair_in = f"[ANONYMIZED PROFILE]\n{p_str}\n\n[SPECIALIST REPORTS]\n{json.dumps(reports, ensure_ascii=False)}"
        final = call_poe_json(client, active_models["chief_scout"], AGENT_SPECS["chief_scout"]["prompt"], chair_in)

        if "error" in final:
            st.session_state.agent_states["chief_scout"] = {"status": "ERROR", "bubble": str(final["error"])[:38], "badge": ""}
        else:
            dec = str(final.get("decision", "PASS")).upper()
            inv_score = final.get("investment_score", "?")
            st.session_state.agent_states["chief_scout"] = {
                "status": "DONE",
                "bubble": f"Score: {inv_score}/100",
                "badge": dec if dec in ["BUY", "PASS"] else "",
            }
        with office_placeholder:
            render_pixel_office(st.session_state.agent_states, active_models, pid)

        st.session_state.latest_single_eval = {
            "pid": pid,
            "profile": profile,
            "reports": reports,
            "final": final,
            "models": dict(active_models),
        }

    if "latest_single_eval" in st.session_state:
        ev = st.session_state.latest_single_eval
        pid, profile, reports, final, used_models = ev["pid"], ev["profile"], ev["reports"], ev["final"], ev["models"]
        radar_svg = build_radar_svg(reports, final)

        st.divider()
        dec_str = str(final.get("decision", "PASS")).upper()
        banner_cls = "verdict-buy" if dec_str == "BUY" else "verdict-pass"
        badge_style = "background:#065F46;color:#fff;" if dec_str == "BUY" else "background:#991B1B;color:#fff;"
        safe_reason = html.escape(str(final.get("key_reason", final.get("error", "No rationale provided."))))
        safe_score = html.escape(str(final.get("investment_score", "?")))

        v_col, r_col = st.columns([1.45, 1], gap="medium")
        with v_col:
            st.markdown(
                f'<div class="verdict-banner {banner_cls}">'
                f'<div style="font-family:\'JetBrains Mono\',monospace; font-size:11px; letter-spacing:0.06em; color:#64748B; font-weight:600;">'
                f'INVESTMENT COMMITTEE VERDICT · {html.escape(pid)}</div>'
                f'<div style="font-size:24px; font-weight:700; color:#0F172A; margin:10px 0; display:flex; align-items:center; gap:12px;">'
                f'<span style="{badge_style} padding:3px 12px; border-radius:6px; font-size:15px;">{html.escape(dec_str)}</span>'
                f'<span>Score: {safe_score} / 100</span></div>'
                f'<p style="font-size:14px; color:#1E293B; margin:0 0 14px 0;">{safe_reason}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            dl1, dl2 = st.columns(2, gap="small")
            report_html = build_scouting_report_html(pid, reports, final, radar_svg, used_models)
            report_md = build_scouting_report_md(pid, profile, reports, final, used_models)
            with dl1:
                st.download_button(
                    label="📄 Export Visual Report (.html)",
                    data=report_html.encode("utf-8"),
                    file_name=f"scouting_report_{pid}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            with dl2:
                st.download_button(
                    label="📝 Export Paper Report (.md)",
                    data=report_md.encode("utf-8"),
                    file_name=f"scouting_report_{pid}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        with r_col:
            st.markdown(
                f'<div class="editorial-card" style="padding:14px 16px;">'
                f'<div style="font-family:\'JetBrains Mono\',monospace; font-size:11px; color:#065F46; font-weight:600; text-align:center; margin-bottom:2px;">'
                f'5-AXIS SCOUTING RADAR</div>{radar_svg}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="medium")
        t_rep, v_rep, r_rep = reports["tech"], reports["valuation"], reports["risk"]

        with c1:
            st.markdown(
                f'<div class="editorial-card">'
                f'<div class="card-header"><span class="card-title">Tech Scout</span>'
                f'<span class="score-pill pill-blue">{html.escape(str(t_rep.get("tech_score", "?")))} / 10</span></div>'
                f'<p style="font-size:13px; color:#334155;">{html.escape(str(t_rep.get("summary", t_rep.get("error", ""))))}</p>'
                f'<div class="section-label">Strengths</div><div>{render_tags(t_rep.get("strengths", []))}</div>'
                f'<div class="section-label">Weaknesses</div><div>{render_tags(t_rep.get("weaknesses", []), "warn")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f'<div class="editorial-card">'
                f'<div class="card-header"><span class="card-title">Valuation Analyst</span>'
                f'<span class="score-pill pill-amber">{html.escape(str(v_rep.get("value_score", "?")))} / 10</span></div>'
                f'<p style="font-size:13px; color:#334155;">{html.escape(str(v_rep.get("summary", v_rep.get("error", ""))))}</p>'
                f'<div class="section-label">5-Year Fair Multiple</div>'
                f'<div><span class="tag-chip mono">{html.escape(str(v_rep.get("fair_multiple_5y", "?")))}x</span></div>'
                f'<div class="section-label">Upside Case</div>'
                f'<p style="font-size:12.5px; color:#334155; margin:0;">{html.escape(str(v_rep.get("upside_case", "N/A")))}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown(
                f'<div class="editorial-card">'
                f'<div class="card-header"><span class="card-title">Risk Skeptic</span>'
                f'<span class="score-pill pill-red">Risk {html.escape(str(r_rep.get("bust_risk_score", "?")))} / 10</span></div>'
                f'<p style="font-size:13px; color:#334155;">{html.escape(str(r_rep.get("summary", r_rep.get("error", ""))))}</p>'
                f'<div class="section-label">Red Flags</div><div>{render_tags(r_rep.get("red_flags", []), "warn")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        with st.expander("Raw JSON Output"):
            st.json({"reports": reports, "final": final})


# ==========================================
# Mode 2: L4 Canary Leakage Audit (4-Agent)
# ==========================================
elif mode == "2. L4 Canary Audit (4-Agent)":
    st.subheader("L4 Canary Leakage Audit")
    st.write("Verify whether any of the 4 judges can identify real footballers from anonymized data before running experiments.")

    tab_single, tab_batch = st.tabs(["Single Profile Audit", "Batch Cohort Audit (Paper Table)"])

    with tab_single:
        if "canary_editor" not in st.session_state:
            first_k = list(SAMPLE_PLAYERS.keys())[0]
            st.session_state.canary_editor = json.dumps(SAMPLE_PLAYERS[first_k], ensure_ascii=False, indent=2)
            st.session_state.last_canary_sample = first_k

        u1, u2 = st.columns(2, gap="medium")
        with u1:
            up_c = st.file_uploader("Upload Profile (.json)", type=["json"], key="canary_single_up")
            if up_c is not None:
                try:
                    obj = json.load(up_c)
                    if isinstance(obj, list) and len(obj) > 0:
                        obj = obj[0]
                    st.session_state.canary_editor = json.dumps(obj, ensure_ascii=False, indent=2)
                except Exception as e:
                    st.error(f"Parse error: {e}")
        with u2:
            c_sample = st.selectbox("Preset Sample", list(SAMPLE_PLAYERS.keys()), key="canary_sel")
            if c_sample != st.session_state.last_canary_sample:
                st.session_state.last_canary_sample = c_sample
                st.session_state.canary_editor = json.dumps(SAMPLE_PLAYERS[c_sample], ensure_ascii=False, indent=2)

        canary_text = st.text_area("Profile Payload (JSON)", key="canary_editor", height=180)

        b1, b2 = st.columns([1, 2], gap="medium")
        with b1:
            st.button(
                "Auto-Anonymize (L2 + L3)",
                key="canary_anon_btn",
                on_click=handle_auto_anonymize,
                args=("canary_editor",),
                use_container_width=True,
            )
        with b2:
            run_c_single = st.button("Run 4-Agent Identity Check", type="primary", use_container_width=True)

        if run_c_single:
            try:
                prof = json.loads(canary_text)
            except json.JSONDecodeError as e:
                st.error(f"JSON Error: {e}")
                st.stop()

            client = get_poe_client(poe_api_key)
            pid = str(prof.get("player_id", "Unknown_Player"))
            st.session_state.current_player_id = f"{pid} (L4 Audit)"

            for r in AGENT_SPECS.keys():
                st.session_state.agent_states[r] = {"status": "WORKING", "bubble": "Auditing...", "badge": ""}
            with office_placeholder:
                render_pixel_office(st.session_state.agent_states, active_models, st.session_state.current_player_id)

            res_4 = run_4agent_canary(client, active_models, json.dumps(prof, ensure_ascii=False, indent=2))

            for r, rep in res_4.items():
                if "error" in rep:
                    st.session_state.agent_states[r] = {"status": "ERROR", "bubble": str(rep["error"])[:36], "badge": ""}
                else:
                    can_id = bool(rep.get("can_identify", False))
                    top1 = rep.get("top3_guesses", ["None"])[0] if isinstance(rep.get("top3_guesses"), list) and rep.get("top3_guesses") else "None"
                    st.session_state.agent_states[r] = {
                        "status": "DONE",
                        "bubble": f"Guess: {top1}",
                        "badge": "LEAK?" if can_id else "SAFE",
                    }
            with office_placeholder:
                render_pixel_office(st.session_state.agent_states, active_models, st.session_state.current_player_id)

            st.divider()
            render_4agent_canary_cards(res_4, active_models)

    with tab_batch:
        canary_batch_file = st.file_uploader("Upload Cohort (.json / .csv)", type=["json", "csv"], key="canary_batch_up")
        if canary_batch_file is not None:
            try:
                if canary_batch_file.name.lower().endswith(".csv"):
                    c_players = pd.read_csv(canary_batch_file).to_dict(orient="records")
                else:
                    raw_c = json.load(canary_batch_file)
                    c_players = raw_c if isinstance(raw_c, list) else [raw_c]
            except Exception as e:
                st.error(f"Failed to read file: {e}")
                st.stop()

            st.info(f"Loaded {len(c_players)} profiles.")
            apply_c_anon = st.checkbox("Apply L2/L3 Auto-Anonymization before auditing", value=False, key="canary_batch_anon")

            if st.button("Run 4-Agent Batch Canary Audit", type="primary"):
                client = get_poe_client(poe_api_key)
                prog = st.progress(0)
                st_msg = st.empty()
                audit_rows = []
                audit_jsonl = []

                for idx, p in enumerate(c_players):
                    if apply_c_anon:
                        p, _ = anonymize_profile(p)
                    pid = str(p.get("player_id", f"Player_{idx+1}"))
                    st_msg.caption(f"Auditing ({idx + 1}/{len(c_players)}): {pid}")
                    p_str = json.dumps(p, ensure_ascii=False, indent=2)

                    res_4 = run_4agent_canary(client, active_models, p_str)
                    audit_jsonl.append(json.dumps({"player_id": pid, "canary_audit": res_4}, ensure_ascii=False))

                    row = {"player_id": pid}
                    any_flag = False
                    for r_key, short_name in [
                        ("tech_scout", "Tech"),
                        ("valuation_analyst", "Valuation"),
                        ("risk_skeptic", "Risk"),
                        ("chief_scout", "Chief"),
                    ]:
                        rep = res_4.get(r_key, {})
                        can_id = bool(rep.get("can_identify", False))
                        if can_id:
                            any_flag = True
                        guesses = rep.get("top3_guesses", [])
                        g_str = ", ".join([str(x) for x in guesses[:3]]) if isinstance(guesses, list) else str(guesses)
                        row[f"{short_name}_CanID"] = "YES" if can_id else "NO"
                        row[f"{short_name}_Top3"] = g_str
                    row["Status"] = "FLAGGED" if any_flag else "CLEAN"
                    audit_rows.append(row)
                    prog.progress((idx + 1) / len(c_players))

                audit_df = pd.DataFrame(audit_rows)
                flagged_cnt = int((audit_df["Status"] == "FLAGGED").sum())
                st_msg.success(f"Audit complete: {len(audit_df) - flagged_cnt}/{len(audit_df)} profiles CLEAN.")

                k1, k2, k3 = st.columns(3)
                k1.metric("Audited", len(audit_df))
                k2.metric("Clean Profiles", len(audit_df) - flagged_cnt)
                k3.metric("Flag Rate", f"{(flagged_cnt / len(audit_df)):.1%}" if len(audit_df) else "0.0%")

                st.dataframe(audit_df, use_container_width=True)

                d1, d2 = st.columns(2)
                with d1:
                    st.download_button(
                        label="Download Audit Table (CSV)",
                        data=audit_df.to_csv(index=False).encode("utf-8-sig"),
                        file_name="canary_audit_table.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                with d2:
                    st.download_button(
                        label="Download Raw Log (JSONL)",
                        data="\n".join(audit_jsonl),
                        file_name="canary_audit_log.jsonl",
                        mime="application/jsonl",
                        use_container_width=True,
                    )


# ==========================================
# Mode 3: Batch Backtest
# ==========================================
elif mode == "3. Batch Backtest":
    st.subheader("Batch Historical Backtest")
    st.write("Upload your anonymized cohort (`players_anon_30.json` or `.csv`) to run the 4-Agent committee across all players.")
    uploaded_file = st.file_uploader("Upload Cohort Data (.json / .csv)", type=["json", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                players = pd.read_csv(uploaded_file).to_dict(orient="records")
            else:
                raw_data = json.load(uploaded_file)
                players = raw_data if isinstance(raw_data, list) else [raw_data]
        except Exception as e:
            st.error(f"Failed to read file: {e}")
            st.stop()

        st.info(f"Loaded {len(players)} player profiles.")
        apply_batch_anon = st.checkbox("Apply L2/L3 Auto-Anonymization before running", value=False)

        with st.expander("Preview Data (First 5 Rows)"):
            st.dataframe(pd.DataFrame(players).head(5), use_container_width=True)

        if st.button("Run Batch Backtest", type="primary"):
            client = get_poe_client(poe_api_key)
            progress = st.progress(0)
            status_text = st.empty()
            results_jsonl = []
            summary_rows = []

            for idx, p in enumerate(players):
                if apply_batch_anon:
                    p, _ = anonymize_profile(p)
                pid = str(p.get("player_id", f"Player_{idx+1}"))
                status_text.caption(f"Evaluating ({idx + 1}/{len(players)}): {pid}")
                p_str = json.dumps(p, ensure_ascii=False, indent=2)

                with ThreadPoolExecutor(max_workers=3) as ex:
                    f1 = ex.submit(call_poe_json, client, active_models["tech_scout"], AGENT_SPECS["tech_scout"]["prompt"], p_str)
                    f2 = ex.submit(call_poe_json, client, active_models["valuation_analyst"], AGENT_SPECS["valuation_analyst"]["prompt"], p_str)
                    f3 = ex.submit(call_poe_json, client, active_models["risk_skeptic"], AGENT_SPECS["risk_skeptic"]["prompt"], p_str)
                    reports = {"tech": f1.result(), "valuation": f2.result(), "risk": f3.result()}

                chair_in = f"[ANONYMIZED PROFILE]\n{p_str}\n\n[SPECIALIST REPORTS]\n{json.dumps(reports, ensure_ascii=False)}"
                final = call_poe_json(client, active_models["chief_scout"], AGENT_SPECS["chief_scout"]["prompt"], chair_in)

                record = {"player_id": pid, "reports": reports, "final": final}
                results_jsonl.append(json.dumps(record, ensure_ascii=False))
                summary_rows.append({
                    "player_id": pid,
                    "decision": str(final.get("decision", "PASS")).upper(),
                    "investment_score": final.get("investment_score", None),
                    "tech_score": reports["tech"].get("tech_score", None),
                    "value_score": reports["valuation"].get("value_score", None),
                    "bust_risk": reports["risk"].get("bust_risk_score", None),
                })
                progress.progress((idx + 1) / len(players))

            st.session_state.latest_batch_df = pd.DataFrame(summary_rows)
            status_text.success("Batch complete. Download JSONL below or proceed to Mode 4 for Ground Truth evaluation.")
            st.dataframe(st.session_state.latest_batch_df, use_container_width=True)

            st.download_button(
                label="Download scouting_results.jsonl",
                data="\n".join(results_jsonl),
                file_name="scouting_results.jsonl",
                mime="application/jsonl",
            )


# ==========================================
# Mode 4: Backtest Evaluation (Truth vs. AI + One-Click Comparison Table)
# ==========================================
elif mode == "4. Backtest Evaluation":
    st.subheader("Backtest Evaluation: Ground Truth vs. AI")
    st.write("Compare AI decisions (`scouting_results.jsonl`) against isolated Ground Truth (`ground_truth_30.csv`) and export ready-to-use comparison tables.")

    col_pred, col_truth = st.columns(2, gap="large")

    pred_df = None
    with col_pred:
        st.markdown("#### 1. AI Predictions")
        use_session = False
        if "latest_batch_df" in st.session_state and not st.session_state.latest_batch_df.empty:
            use_session = st.checkbox("Use latest Mode 3 session results", value=True)

        if use_session:
            pred_df = st.session_state.latest_batch_df.copy()
            st.caption(f"Loaded {len(pred_df)} predictions from active session.")
        else:
            pred_file = st.file_uploader("Upload AI Results (.jsonl / .csv)", type=["jsonl", "csv"], key="eval_pred")
            if pred_file is not None:
                try:
                    if pred_file.name.lower().endswith(".csv"):
                        pred_df = pd.read_csv(pred_file)
                    else:
                        rows = []
                        for line in pred_file.getvalue().decode("utf-8").splitlines():
                            if line.strip():
                                rec = json.loads(line)
                                fin = rec.get("final", {})
                                reps = rec.get("reports", {})
                                rows.append({
                                    "player_id": str(rec.get("player_id", "")),
                                    "decision": str(fin.get("decision", "PASS")).upper(),
                                    "investment_score": fin.get("investment_score", None),
                                    "tech_score": reps.get("tech", {}).get("tech_score", None),
                                    "value_score": reps.get("valuation", {}).get("value_score", None),
                                    "bust_risk": reps.get("risk", {}).get("bust_risk_score", None),
                                })
                        pred_df = pd.DataFrame(rows)
                    st.caption(f"Loaded {len(pred_df)} AI predictions.")
                except Exception as e:
                    st.error(f"Parse error: {e}")

    truth_df = None
    with col_truth:
        st.markdown("#### 2. Ground Truth")
        truth_file = st.file_uploader("Upload Ground Truth (.csv / .json)", type=["csv", "json"], key="eval_truth")
        if truth_file is not None:
            try:
                if truth_file.name.lower().endswith(".csv"):
                    truth_df = pd.read_csv(truth_file)
                else:
                    raw_t = json.load(truth_file)
                    truth_df = pd.DataFrame(raw_t if isinstance(raw_t, list) else [raw_t])
                st.caption(f"Loaded {len(truth_df)} Ground Truth records.")
            except Exception as e:
                st.error(f"Parse error: {e}")

    if pred_df is not None and truth_df is not None:
        st.divider()
        t_cols = list(truth_df.columns)

        def guess_col(candidates, fallback_idx=0):
            for c in candidates:
                for col in t_cols:
                    if col.lower() == c:
                        return t_cols.index(col)
            return min(fallback_idx, len(t_cols) - 1)

        m1, m2, m3 = st.columns(3, gap="medium")
        with m1:
            id_col = st.selectbox("Player ID Column", t_cols, index=guess_col(["player_id", "id"], 0))
        with m2:
            label_col = st.selectbox("Outcome Label (Hit/Miss or 1/0)", t_cols, index=guess_col(["actual_label", "label", "outcome", "hit"], 1))
        with m3:
            roi_col = st.selectbox("5Y Value Multiple (e.g., 3.5)", t_cols, index=guess_col(["roi_multiple", "multiple_5y", "return_multiple", "value_multiple"], 2))

        pred_df["player_id"] = pred_df["player_id"].astype(str).str.strip()
        truth_clean = truth_df[[id_col, label_col, roi_col]].copy()
        truth_clean.columns = ["player_id", "actual_label", "roi_multiple"]
        truth_clean["player_id"] = truth_clean["player_id"].astype(str).str.strip()
        truth_clean["roi_multiple"] = pd.to_numeric(truth_clean["roi_multiple"], errors="coerce")

        merged = pd.merge(pred_df, truth_clean, on="player_id", how="inner")

        if merged.empty:
            st.warning("No matching `player_id` found. Please verify ID formatting.")
        else:
            merged["is_hit"] = merged["actual_label"].astype(str).str.strip().str.lower().isin(["hit", "1", "true", "yes", "buy"])
            merged["is_buy"] = merged["decision"].astype(str).str.strip().str.upper() == "BUY"
            merged["investment_score"] = pd.to_numeric(merged["investment_score"], errors="coerce")

            def match_tag(row):
                if row["is_buy"] and row["is_hit"]:
                    return "TP (Hit Bought)"
                if row["is_buy"] and not row["is_hit"]:
                    return "FP (Bust Bought)"
                if not row["is_buy"] and not row["is_hit"]:
                    return "TN (Bust Avoided)"
                return "FN (Missed Hit)"

            merged["Match_Result"] = merged.apply(match_tag, axis=1)

            tp = int((merged["is_buy"] & merged["is_hit"]).sum())
            fp = int((merged["is_buy"] & ~merged["is_hit"]).sum())
            tn = int((~merged["is_buy"] & ~merged["is_hit"]).sum())
            fn = int((~merged["is_buy"] & merged["is_hit"]).sum())

            total = len(merged)
            accuracy = (tp + tn) / total if total else 0.0
            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

            buy_df = merged[merged["is_buy"]]
            ai_mult = buy_df["roi_multiple"].mean() if not buy_df.empty else 1.0
            all_mult = merged["roi_multiple"].mean()
            ai_roi_pct = (ai_mult - 1.0) * 100
            all_roi_pct = (all_mult - 1.0) * 100
            alpha_pct = ai_roi_pct - all_roi_pct

            k_val = min(10, max(1, len(merged) // 2))
            ranked = merged.dropna(subset=["investment_score", "roi_multiple"]).sort_values("investment_score", ascending=False)
            top_k_df = ranked.head(k_val)
            bot_k_df = ranked.tail(k_val)
            top_k_mult = top_k_df["roi_multiple"].mean() if not top_k_df.empty else 1.0
            bot_k_mult = bot_k_df["roi_multiple"].mean() if not bot_k_df.empty else 1.0

            strategy_comp_df = pd.DataFrame([
                {
                    "Strategy": "4-Agent Committee (BUY Portfolio)",
                    "Players_Selected": len(buy_df),
                    "Hit_Rate_Precision": f"{precision:.1%}",
                    "Avg_5Y_Multiple": round(ai_mult, 2),
                    "5Y_ROI_Pct": f"{ai_roi_pct:+.1f}%",
                    "Alpha_vs_BuyAll": f"{alpha_pct:+.1f}%",
                },
                {
                    "Strategy": "Buy-All Market Benchmark",
                    "Players_Selected": total,
                    "Hit_Rate_Precision": f"{merged['is_hit'].mean():.1%}",
                    "Avg_5Y_Multiple": round(all_mult, 2),
                    "5Y_ROI_Pct": f"{all_roi_pct:+.1f}%",
                    "Alpha_vs_BuyAll": "0.0%",
                },
                {
                    "Strategy": f"Top-{k_val} Scored Cohort",
                    "Players_Selected": len(top_k_df),
                    "Hit_Rate_Precision": f"{top_k_df['is_hit'].mean():.1%}" if not top_k_df.empty else "0.0%",
                    "Avg_5Y_Multiple": round(top_k_mult, 2),
                    "5Y_ROI_Pct": f"{(top_k_mult - 1.0) * 100:+.1f}%",
                    "Alpha_vs_BuyAll": f"{(top_k_mult - all_mult) * 100:+.1f}%",
                },
                {
                    "Strategy": f"Bottom-{k_val} Scored Cohort",
                    "Players_Selected": len(bot_k_df),
                    "Hit_Rate_Precision": f"{bot_k_df['is_hit'].mean():.1%}" if not bot_k_df.empty else "0.0%",
                    "Avg_5Y_Multiple": round(bot_k_mult, 2),
                    "5Y_ROI_Pct": f"{(bot_k_mult - 1.0) * 100:+.1f}%",
                    "Alpha_vs_BuyAll": f"{(bot_k_mult - all_mult) * 100:+.1f}%",
                },
            ])

            st.markdown("### Performance Summary")
            k1, k2, k3, k4 = st.columns(4, gap="medium")
            k1.metric("Precision (BUY Hit Rate)", f"{precision:.1%}", f"{tp}/{tp+fp} Hits")
            k2.metric("Accuracy", f"{accuracy:.1%}", f"F1: {f1:.2f}")
            k3.metric("AI Portfolio 5Y ROI", f"{ai_roi_pct:+.1f}%", f"{ai_mult:.2f}x avg")
            k4.metric("Alpha vs. Buy-All", f"{alpha_pct:+.1f}%", f"Bench: {all_roi_pct:+.1f}%")

            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Strategy Comparison Table")
            st.dataframe(strategy_comp_df, use_container_width=True, hide_index=True)

            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
            ch1, ch2 = st.columns(2, gap="large")

            with ch1:
                st.markdown("#### Confusion Matrix")
                cm_df = pd.DataFrame(
                    [[tp, fp], [fn, tn]],
                    index=["Actual Hit (≥3x)", "Actual Miss (<1.2x)"],
                    columns=["AI: BUY", "AI: PASS"],
                )
                st.dataframe(cm_df, use_container_width=True)

            with ch2:
                st.markdown("#### Top-K vs. Bottom-K Stratified Return")
                if len(ranked) >= 2:
                    strat_df = pd.DataFrame(
                        {"Avg 5Y Multiple (x)": [top_k_mult, all_mult, bot_k_mult]},
                        index=[f"Top-{k_val} Scored", "Buy-All", f"Bottom-{k_val} Scored"],
                    )
                    st.bar_chart(strat_df, color="#065F46")

            st.markdown("#### Player-by-Player AI vs. Ground Truth Table")
            export_cols = [c for c in ["player_id", "decision", "investment_score", "tech_score", "value_score", "bust_risk", "actual_label", "roi_multiple", "Match_Result"] if c in merged.columns]
            final_table = merged[export_cols].sort_values("investment_score", ascending=False)
            st.dataframe(final_table, use_container_width=True, hide_index=True)

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            md_comp = (
                f"# Backtest Evaluation Comparison Report\n\n"
                f"**Classification Metrics:** Accuracy `{accuracy:.1%}` | Precision `{precision:.1%}` | Recall `{recall:.1%}` | F1 `{f1:.2f}`\n\n"
                f"## 1. Strategy Performance Comparison\n"
                + df_to_md(strategy_comp_df)
                + f"\n\n## 2. Player-by-Player Comparison\n"
                + df_to_md(final_table)
            )
            e1, e2, e3 = st.columns(3, gap="small")
            with e1:
                st.download_button(
                    label="📊 Export Player Comparison (.csv)",
                    data=final_table.to_csv(index=False).encode("utf-8-sig"),
                    file_name="ai_vs_truth_comparison.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with e2:
                st.download_button(
                    label="📈 Export Strategy Summary (.csv)",
                    data=strategy_comp_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="strategy_comparison_summary.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with e3:
                st.download_button(
                    label="📝 Export Paper Table (.md)",
                    data=md_comp.encode("utf-8"),
                    file_name="backtest_comparison_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
