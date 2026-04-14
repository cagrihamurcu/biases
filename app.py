import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="FinTechX Bias Challenge",
    page_icon="📈",
    layout="wide",
)


# -----------------------------
# Constants
# -----------------------------
TIME_LIMIT_SECONDS = 5 * 60
LEADERBOARD_FILE = Path(__file__).with_name("fintechx_leaderboard.json")
APP_VERSION = "2.0"


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    :root {
        --bg-1: #0f172a;
        --bg-2: #111827;
        --card: rgba(255,255,255,0.06);
        --border: rgba(255,255,255,0.12);
        --text: #e5eefc;
        --muted: #9fb0d0;
        --accent: #7c3aed;
        --accent-2: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(124, 58, 237, 0.16), transparent 28%),
            radial-gradient(circle at top right, rgba(6, 182, 212, 0.14), transparent 30%),
            linear-gradient(135deg, var(--bg-1), var(--bg-2));
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    h1, h2, h3, h4, h5, h6, p, li, label, div {
        color: var(--text);
    }

    .hero {
        padding: 1.5rem 1.6rem;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(124,58,237,.24), rgba(6,182,212,.16));
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 20px 60px rgba(0,0,0,0.22);
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .hero p {
        margin: 0.6rem 0 0 0;
        color: #dbe7ff;
        font-size: 1rem;
    }

    .glass-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 1rem 1.1rem;
        box-shadow: 0 14px 36px rgba(0,0,0,0.18);
    }

    .mini-stat {
        padding: 1rem 1.1rem;
        border-radius: 20px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        min-height: 112px;
    }

    .mini-stat .label {
        color: var(--muted);
        font-size: 0.86rem;
        margin-bottom: 0.35rem;
    }

    .mini-stat .value {
        font-size: 1.9rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .mini-stat .sub {
        color: #d7def0;
        font-size: 0.9rem;
        margin-top: 0.4rem;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
    }

    .section-sub {
        color: var(--muted);
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }

    .name-chip {
        display: inline-block;
        padding: 0.45rem 0.75rem;
        border-radius: 999px;
        background: rgba(16,185,129,0.16);
        border: 1px solid rgba(16,185,129,0.35);
        color: #dffaf0;
        font-size: 0.92rem;
        margin: 0.2rem 0.35rem 0.2rem 0;
        font-weight: 650;
    }

    .name-chip.playing {
        background: rgba(59,130,246,0.12);
        border-color: rgba(59,130,246,0.3);
        color: #dbeafe;
    }

    .name-chip.finished {
        background: rgba(16,185,129,0.14);
        border-color: rgba(16,185,129,0.32);
    }

    .name-chip.timeout {
        background: rgba(239,68,68,0.14);
        border-color: rgba(239,68,68,0.3);
        color: #fee2e2;
    }

    .question-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 1.1rem;
        margin-bottom: 1rem;
    }

    .question-badge {
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 700;
        color: #cbd5e1;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        padding: 0.35rem 0.55rem;
        border-radius: 999px;
        background: rgba(124,58,237,0.18);
        border: 1px solid rgba(124,58,237,0.28);
        margin-bottom: 0.65rem;
    }

    .timer-box {
        background: linear-gradient(135deg, rgba(239,68,68,0.16), rgba(245,158,11,0.16));
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 0.85rem 1rem;
        min-height: 90px;
    }

    .timer-label {
        color: var(--muted);
        font-size: 0.82rem;
        margin-bottom: 0.2rem;
    }

    .result-good {
        border-left: 4px solid var(--success);
    }

    .result-warn {
        border-left: 4px solid var(--warning);
    }

    .result-bad {
        border-left: 4px solid var(--danger);
    }

    .footer-note {
        color: var(--muted);
        font-size: 0.88rem;
    }

    div[data-testid="stMetricValue"] {
        color: white;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 20px;
        overflow: hidden;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.14);
        background: linear-gradient(135deg, rgba(124,58,237,0.88), rgba(6,182,212,0.85));
        color: white;
        font-weight: 700;
        padding: 0.7rem 1rem;
    }

    .stTextInput input, .stTextArea textarea {
        border-radius: 14px !important;
    }

    div[data-baseweb="select"] > div,
    div[role="radiogroup"],
    .stSlider {
        background: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Helpers
# -----------------------------

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


EXTERNAL_KEYWORDS = {
    "market",
    "economy",
    "macro",
    "news",
    "volatility",
    "crisis",
    "rates",
    "interest",
    "inflation",
    "regulation",
    "luck",
    "timing",
    "sector",
    "panic",
    "conditions",
    "competition",
    "unexpected",
    "external",
    "government",
    "policy",
    "sentiment",
    "piyasa",
    "ekonomi",
    "haber",
    "şans",
    "sans",
    "kriz",
    "faiz",
    "enflasyon",
    "regülasyon",
    "regulasyon",
    "sektör",
    "sektor",
}

INTERNAL_KEYWORDS = {
    "mistake",
    "error",
    "poor",
    "bad",
    "wrong",
    "careless",
    "greedy",
    "emotional",
    "risky",
    "overconfident",
    "ignored",
    "didn't research",
    "did not research",
    "no research",
    "discipline",
    "strategy",
    "decision",
    "impatient",
    "misread",
    "hata",
    "yanlış",
    "yanlis",
    "dikkatsiz",
    "açgözlü",
    "acgozlu",
    "duygusal",
    "riskli",
    "özgüven",
    "ozguven",
    "araştır",
    "arastir",
    "disiplin",
    "strateji",
    "karar",
}

LIKERT_SCORE = {
    "Strongly agree": 5,
    "Agree": 4,
    "Undecided": 3,
    "Disagree": 2,
    "Strongly disagree": 1,
}


if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "game_submitted" not in st.session_state:
    st.session_state.game_submitted = False
if "start_ts" not in st.session_state:
    st.session_state.start_ts = None
if "result_payload" not in st.session_state:
    st.session_state.result_payload = None


# -----------------------------
# Persistence
# -----------------------------

def load_store() -> Dict[str, Dict]:
    if not LEADERBOARD_FILE.exists():
        return {}
    try:
        return json.loads(LEADERBOARD_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}



def save_store(data: Dict[str, Dict]) -> None:
    LEADERBOARD_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )



def player_key(name: str) -> str:
    return normalize_text(name)



def register_player(name: str) -> None:
    store = load_store()
    key = player_key(name)
    now = time.time()
    existing = store.get(key, {})
    store[key] = {
        "name": name.strip(),
        "status": "Playing",
        "score": existing.get("score"),
        "elapsed_seconds": existing.get("elapsed_seconds"),
        "submitted_at": existing.get("submitted_at"),
        "started_at": now,
        "version": APP_VERSION,
    }
    save_store(store)



def mark_timeout(name: str, elapsed_seconds: int) -> None:
    store = load_store()
    key = player_key(name)
    if key in store:
        store[key]["status"] = "Time up"
        store[key]["elapsed_seconds"] = elapsed_seconds
        store[key]["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        store[key] = {
            "name": name.strip(),
            "status": "Time up",
            "score": None,
            "elapsed_seconds": elapsed_seconds,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "started_at": time.time() - elapsed_seconds,
            "version": APP_VERSION,
        }
    save_store(store)



def finish_player(name: str, score: int, elapsed_seconds: int) -> None:
    store = load_store()
    key = player_key(name)
    previous = store.get(key, {})
    prev_score = previous.get("score")
    prev_elapsed = previous.get("elapsed_seconds")

    should_update = False
    if prev_score is None:
        should_update = True
    elif score > int(prev_score):
        should_update = True
    elif score == int(prev_score) and (prev_elapsed is None or elapsed_seconds < int(prev_elapsed)):
        should_update = True

    if should_update:
        store[key] = {
            "name": name.strip(),
            "status": "Finished",
            "score": int(score),
            "elapsed_seconds": int(elapsed_seconds),
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "started_at": previous.get("started_at", time.time() - elapsed_seconds),
            "version": APP_VERSION,
        }
    else:
        # keep best score but update visible status
        previous["status"] = "Finished"
        store[key] = previous

    save_store(store)



def format_seconds(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02d}:{secs:02d}"



def get_leaderboard_rows() -> List[Dict[str, str | int]]:
    store = load_store()
    finished = [item for item in store.values() if item.get("status") == "Finished" and item.get("score") is not None]
    finished.sort(key=lambda x: (-int(x["score"]), int(x.get("elapsed_seconds") or 999999), x["name"].lower()))

    rows: List[Dict[str, str | int]] = []
    for idx, item in enumerate(finished, start=1):
        badge = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else str(idx)
        rows.append(
            {
                "Rank": badge,
                "Name": item["name"],
                "Score": int(item["score"]),
                "Time": format_seconds(item.get("elapsed_seconds")),
                "Submitted": item.get("submitted_at", "—"),
            }
        )
    return rows



def get_participant_chips() -> str:
    store = load_store()
    participants = list(store.values())
    participants.sort(key=lambda x: (x.get("status") != "Playing", x["name"].lower()))
    chips: List[str] = []
    for item in participants:
        status = item.get("status", "Playing")
        css_class = "playing" if status == "Playing" else "finished" if status == "Finished" else "timeout"
        icon = "🟦" if status == "Playing" else "🟩" if status == "Finished" else "🟥"
        chips.append(f'<span class="name-chip {css_class}">{icon} {item["name"]}</span>')
    return "".join(chips) if chips else '<span class="footer-note">No participants yet.</span>'


# -----------------------------
# Analysis helpers
# -----------------------------

def keyword_hits(text: str, keywords: set) -> int:
    t = normalize_text(text)
    return sum(1 for kw in keywords if kw in t)



def analyze_attribution(self_text: str, friend_text: str) -> Tuple[str, str, int]:
    self_external = keyword_hits(self_text, EXTERNAL_KEYWORDS)
    self_internal = keyword_hits(self_text, INTERNAL_KEYWORDS)
    friend_external = keyword_hits(friend_text, EXTERNAL_KEYWORDS)
    friend_internal = keyword_hits(friend_text, INTERNAL_KEYWORDS)

    if (self_external >= self_internal + 1) and (friend_internal >= friend_external + 1):
        return (
            "Strong self-serving bias signal",
            "You seem more likely to explain your own loss with outside factors, while explaining your friend's loss with personal mistakes.",
            4,
        )
    if (self_external > self_internal) and (friend_internal > friend_external):
        return (
            "Moderate self-serving bias signal",
            "Your wording suggests a softer version of the same pattern: external reasons for yourself, internal reasons for your friend.",
            8,
        )
    if (self_internal > self_external) and (friend_internal > friend_external):
        return (
            "More self-critical pattern",
            "You appear willing to assign personal responsibility to both yourself and your friend, which can reduce self-serving bias.",
            12,
        )
    if (self_external > self_internal) and (friend_external > friend_internal):
        return (
            "External attribution pattern",
            "You seem to explain losses mainly through outside conditions for both people. This may reduce blame, but it can also hide decision errors.",
            9,
        )
    return (
        "Mixed attribution pattern",
        "Your answers do not show a clear self-serving pattern. That may mean your reasoning is more balanced, or simply more nuanced than a keyword check can capture.",
        10,
    )



def q1_feedback(value: int) -> Tuple[str, str, int]:
    if 25 <= value <= 45:
        return (
            "Calibrated forecast",
            "Your answer stays closer to real-world uncertainty. That reduces the risk of overconfidence.",
            12,
        )
    if 15 <= value <= 55:
        return (
            "Moderate confidence",
            "Your estimate is still fairly confident, but not extreme.",
            8,
        )
    if value >= 60:
        return (
            "Strong overconfidence signal",
            "A very high forecast may suggest that you are placing a lot of trust in your own forecasting ability.",
            3,
        )
    return (
        "Very cautious forecast",
        "Your answer is highly conservative. This avoids overconfidence, but it may also understate possible upside.",
        7,
    )



def q2_feedback(choice: str) -> Tuple[str, str, int]:
    if choice == "I cannot decide with this information":
        return (
            "Data-conscious response",
            "This answer resists the temptation to build a company forecast from a single narrative cue.",
            12,
        )
    if choice == "Moderate":
        return (
            "Partly cautious response",
            "You are less influenced by the CEO story than someone choosing an extreme answer.",
            8,
        )
    if choice == "Successful":
        return (
            "Representativeness bias signal",
            "You may be inferring that a strong CEO background automatically means a strong company outcome.",
            3,
        )
    return (
        "Narrative-driven negative inference",
        "A strong conclusion from limited information still reflects story-based judgment.",
        4,
    )



def q3_feedback(value: int) -> Tuple[str, str, int]:
    if 12 <= value <= 20:
        return (
            "Anchoring signal",
            "Your estimate is close to last year's 15% growth. This may mean the initial figure became a mental anchor.",
            3,
        )
    if 8 <= value <= 25:
        return (
            "Mild anchoring signal",
            "Your answer is somewhat close to the reference point. The previous year's number may still have influenced you.",
            7,
        )
    return (
        "Lower anchoring signal",
        "Your estimate moved more clearly away from the initial 15% reference point.",
        12,
    )



def q4_feedback(value: int) -> Tuple[str, str, int]:
    if 5 <= value <= 25:
        return (
            "Calmer risk estimate",
            "Your answer suggests that recent headlines did not dominate your estimate as much.",
            12,
        )
    if 26 <= value <= 39:
        return (
            "Possible availability effect",
            "Your answer may still reflect recent negative news, though less strongly.",
            7,
        )
    if value >= 40:
        return (
            "Availability bias signal",
            "A high failure probability may mean recent fintech failure stories became unusually vivid in memory and influenced your judgment.",
            3,
        )
    return (
        "Very low risk estimate",
        "Your estimate resists media salience, though it may also understate uncertainty.",
        9,
    )



def q5_feedback(choice: str) -> Tuple[str, str, int]:
    score = LIKERT_SCORE[choice]
    if score <= 2:
        return (
            "Lower illusion of control signal",
            "Your answer recognizes that information access is not the same as controlling risk.",
            12,
        )
    if score == 3:
        return (
            "Balanced but undecided",
            "You may sense that information matters, while also recognizing that many risks remain outside investor control.",
            8,
        )
    return (
        "Illusion of control signal",
        "Agreeing with this statement may mean you are treating access to information as if it creates control over outcomes.",
        3,
    )



def q6_feedback(choice: str) -> Tuple[str, str, int]:
    if choice == "Audit report":
        return (
            "More analytical response",
            "You are giving more weight to the formal risk signal, even though it may feel less emotionally attractive.",
            12,
        )
    if choice == "Undecided":
        return (
            "Unresolved conflict",
            "This answer shows that contradictory information created genuine tension, which is a normal part of real financial decisions.",
            8,
        )
    return (
        "Cognitive conflict signal",
        "You may be favoring the more human and optimistic message over the tougher but more cautionary audit signal.",
        3,
    )



def q8_feedback(choice: str) -> Tuple[str, str, int]:
    if choice == "No, it was not obvious":
        return (
            "Lower hindsight bias signal",
            "Your answer recognizes that difficult outcomes are often much less obvious before they happen.",
            12,
        )
    if choice == "Not sure":
        return (
            "Partial hindsight resistance",
            "You are not fully rewriting the past, but the event may still feel easier to explain after the fact.",
            8,
        )
    return (
        "Hindsight bias signal",
        "After a failure happens, it is easy to feel that the outcome had been obvious all along.",
        3,
    )


BIAS_DETAILS: Dict[str, Dict[str, List[str] | str]] = {
    "Question 1 – Overconfidence Bias": {
        "observation": "Many students give estimates in the 60% to 90% range.",
        "why": "People often overestimate their analysis skills, market forecasting accuracy, and ability to predict outcomes.",
        "impact": [
            "Taking too much risk",
            "Trading too often",
            "Holding losing positions for too long",
            "Creating excessive portfolio volatility",
            "Under-diversification",
        ],
        "discussion": [
            "What emotion or logic led you to write this number?",
            "Did you think about how difficult a one-year growth forecast actually is?",
            "Compared with a professional analyst, is 80% accuracy really realistic?",
            "How can overconfidence affect investment decisions?",
        ],
    },
    "Question 2 – Representativeness Bias": {
        "observation": "The answer 'Successful' is often the most common choice.",
        "why": "The mind uses a shortcut: 'Good CEO background → good company outcome.' It sounds reasonable, but it is not a sufficient statistical basis.",
        "impact": [
            "Startup bubbles",
            "Too much faith in executive charisma",
            "Opening positions with too little data",
            "Investing in a story instead of performance",
        ],
        "discussion": [
            "What pushed you toward this option?",
            "Is it rational to make a forecast without financial data?",
            "Do real investors make the same mistake?",
        ],
    },
    "Question 3 – Anchoring and Adjustment": {
        "observation": "Most estimates cluster around 12% to 20%.",
        "why": "The first number given becomes a reference point, and people usually adjust away from it too little.",
        "impact": [
            "Analyst target prices converging too closely",
            "Overreliance on past performance",
            "Slow adaptation to new information",
            "Reluctance to rebalance portfolios",
        ],
        "discussion": [
            "Was your estimate close to 15%?",
            "Did you notice that the number influenced you?",
            "If last year's growth had been 40%, how would your estimate change?",
        ],
    },
    "Question 4 – Availability Bias": {
        "observation": "When fintech failures are fresh in the news, students often write much higher failure probabilities.",
        "why": "The mind uses a shortcut: 'What I heard recently is more likely.' Easily recalled information can distort judgment.",
        "impact": [
            "Panic selling during crises",
            "Exaggerated risk perception",
            "Overstating the pricing effect of news sentiment",
        ],
        "discussion": [
            "What news came to mind before answering?",
            "Would your estimate change if those stories were not fresh in memory?",
            "How can investors protect themselves from media influence?",
        ],
    },
    "Question 5 – Illusion of Control": {
        "observation": "Many students agree with the statement.",
        "why": "People often confuse being informed with being in control. Financial statements help, but they do not remove regulation risk, competitive pressure, or macro shocks.",
        "impact": [
            "Taking positions that are too large",
            "Risk-management mistakes driven by overconfidence",
            "Misjudging complex products",
        ],
        "discussion": [
            "Does seeing financial statements really create control?",
            "What is the difference between information and control?",
            "Do even professional investors fall into this trap?",
        ],
    },
    "Question 6 – Cognitive Conflict": {
        "observation": "Many students choose the CFO.",
        "why": "The mind dislikes contradiction. When information conflicts, people often prefer the simpler or more emotionally comfortable message.",
        "impact": [
            "Ignoring bad news",
            "Excessive optimism",
            "Underestimating audit reports",
        ],
        "discussion": [
            "How did the CFO's optimism affect you?",
            "Why is the audit report harder to accept?",
            "Why is it difficult to stay rational when information conflicts?",
        ],
    },
    "Question 7 – Attribution / Self-Serving Bias": {
        "observation": "People often say 'The market was bad' for themselves, but 'They made a mistake' for others.",
        "why": "People protect their self-image by attributing success to themselves and failure to outside factors, while judging others more harshly.",
        "impact": [
            "Failing to learn from personal mistakes",
            "Distorted performance evaluation",
            "Weaker accountability in investing",
        ],
        "discussion": [
            "Why did you avoid blaming yourself?",
            "Why is it easier to blame your friend?",
            "How can this bias affect portfolio managers?",
        ],
    },
    "Question 8 – Hindsight Bias": {
        "observation": "Many people say the result was obvious afterward.",
        "why": "Once an outcome happens, the brain rewrites the past and makes the event look more predictable than it really was.",
        "impact": [
            "Stronger overconfidence",
            "The illusion of 'I already knew it'",
            "Poorer future risk analysis",
        ],
        "discussion": [
            "Was it really obvious at the time?",
            "Why does it feel clearer after the event?",
            "How does this bias affect investor psychology?",
        ],
    },
}


# -----------------------------
# Scoring
# -----------------------------

def build_result_payload(responses: Dict) -> Dict:
    q1_title, q1_text, q1_score = q1_feedback(responses["Q1"])
    q2_title, q2_text, q2_score = q2_feedback(responses["Q2"])
    q3_title, q3_text, q3_score = q3_feedback(responses["Q3"])
    q4_title, q4_text, q4_score = q4_feedback(responses["Q4"])
    q5_title, q5_text, q5_score = q5_feedback(responses["Q5"])
    q6_title, q6_text, q6_score = q6_feedback(responses["Q6"])
    q7_title, q7_text, q7_score = analyze_attribution(responses["Q7a"], responses["Q7b"])
    q8_title, q8_text, q8_score = q8_feedback(responses["Q8"])

    breakdown = [
        {"Question": "Q1", "Bias": "Overconfidence", "Signal": q1_title, "Points": q1_score, "Explanation": q1_text},
        {"Question": "Q2", "Bias": "Representativeness", "Signal": q2_title, "Points": q2_score, "Explanation": q2_text},
        {"Question": "Q3", "Bias": "Anchoring", "Signal": q3_title, "Points": q3_score, "Explanation": q3_text},
        {"Question": "Q4", "Bias": "Availability", "Signal": q4_title, "Points": q4_score, "Explanation": q4_text},
        {"Question": "Q5", "Bias": "Illusion of Control", "Signal": q5_title, "Points": q5_score, "Explanation": q5_text},
        {"Question": "Q6", "Bias": "Cognitive Conflict", "Signal": q6_title, "Points": q6_score, "Explanation": q6_text},
        {"Question": "Q7", "Bias": "Self-Serving Bias", "Signal": q7_title, "Points": q7_score, "Explanation": q7_text},
        {"Question": "Q8", "Bias": "Hindsight Bias", "Signal": q8_title, "Points": q8_score, "Explanation": q8_text},
    ]

    total_score = sum(item["Points"] for item in breakdown)
    return {
        "score": total_score,
        "breakdown": breakdown,
    }


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <h1>FinTechX Bias Challenge</h1>
        <p>A modern classroom game about behavioral finance. Players answer 8 questions in English, race against the clock, and appear on a shared leaderboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.markdown(
        f"""
        <div class="mini-stat">
            <div class="label">Questions</div>
            <div class="value">8</div>
            <div class="sub">Question 7 includes parts A and B.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
        <div class="mini-stat">
            <div class="label">Time Limit</div>
            <div class="value">{TIME_LIMIT_SECONDS // 60} min</div>
            <div class="sub">Fast completion helps as a tiebreaker.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    rows = get_leaderboard_rows()
    st.markdown(
        f"""
        <div class="mini-stat">
            <div class="label">Leaderboard</div>
            <div class="value">{len(rows)}</div>
            <div class="sub">Everyone can see the participant names.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div class="glass-card">
        <div class="section-title">Live participant wall</div>
        <div class="section-sub">Blue = playing, green = finished, red = time up.</div>
        <div>{get_participant_chips()}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")


# -----------------------------
# Start screen
# -----------------------------
if not st.session_state.game_started:
    start_col, info_col = st.columns([1.1, 0.9])

    with start_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Join the game</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-sub">Enter a visible player name. When you start, your name appears in the room and your timer begins immediately.</div>',
            unsafe_allow_html=True,
        )
        with st.form("start_form"):
            player_name = st.text_input(
                "Visible player name",
                placeholder="For example: Ayse K. / Team 3 / Mehmet",
                max_chars=30,
            )
            start_clicked = st.form_submit_button("Start challenge")

        if start_clicked:
            cleaned = player_name.strip()
            if len(cleaned) < 2:
                st.error("Please enter a visible name with at least 2 characters.")
            else:
                st.session_state.player_name = cleaned
                st.session_state.game_started = True
                st.session_state.game_submitted = False
                st.session_state.result_payload = None
                st.session_state.start_ts = time.time()
                register_player(cleaned)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with info_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Scoring logic</div>', unsafe_allow_html=True)
        st.markdown(
            """
            - The app gives more points to answers that show **better bias awareness**.
            - The ranking is sorted by **Score** first, then **completion time**.
            - If a player uses the same name again, the board keeps that player's **best result**.
            """
        )
        st.info("Tip: This is still a learning activity, not a clinical or psychological diagnosis.")
        st.markdown("</div>", unsafe_allow_html=True)

    live_rows = get_leaderboard_rows()
    if live_rows:
        st.write("")
        st.markdown('<div class="section-title">Current ranking</div>', unsafe_allow_html=True)
        st.dataframe(live_rows, use_container_width=True, hide_index=True)
    else:
        st.warning("The ranking table will appear here after the first player finishes.")

    st.stop()


# -----------------------------
# Active game state
# -----------------------------
player_name = st.session_state.player_name
elapsed_seconds = int(time.time() - st.session_state.start_ts)
remaining_seconds = max(0, TIME_LIMIT_SECONDS - elapsed_seconds)
time_is_up = remaining_seconds <= 0 and not st.session_state.game_submitted

status_col, timer_col = st.columns([1.2, 0.8])
with status_col:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">Player status</div>
            <div class="section-sub">You are playing as <strong>{player_name}</strong>. Your name is visible in the shared room and on the final ranking table.</div>
            <div class="name-chip playing">👤 {player_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with timer_col:
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    st.markdown('<div class="timer-box">', unsafe_allow_html=True)
    st.markdown('<div class="timer-label">Time remaining</div>', unsafe_allow_html=True)
    timer_html = f"""
    <div id="countdown" style="font-size:2rem;font-weight:800;color:white;line-height:1.15;">{minutes:02d}:{seconds:02d}</div>
    <div style="color:#dbe7ff;font-size:0.9rem;margin-top:0.35rem;">Auto-enforced max duration: {TIME_LIMIT_SECONDS // 60} minutes</div>
    <script>
    const end = Date.now() + ({remaining_seconds} * 1000);
    const el = document.getElementById("countdown");
    function tick() {{
        const diff = Math.max(0, end - Date.now());
        const total = Math.floor(diff / 1000);
        const m = String(Math.floor(total / 60)).padStart(2, '0');
        const s = String(total % 60).padStart(2, '0');
        if (el) el.textContent = `${{m}}:${{s}}`;
    }}
    tick();
    setInterval(tick, 1000);
    </script>
    """
    components.html(timer_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

if time_is_up:
    mark_timeout(player_name, elapsed_seconds)
    st.error("Time is up. Your attempt has been marked as expired. You can still view the ranking table below.")


# -----------------------------
# Survey
# -----------------------------
if not st.session_state.game_submitted and not time_is_up:
    st.write("")
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Behavioral Finance Survey</div>
            <div class="section-sub">Answer all questions in English. When you submit, the app calculates your bias-awareness score and places you on the leaderboard.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("fintechx_bias_form"):
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 1</div>', unsafe_allow_html=True)
        q1 = st.slider(
            "What do you estimate is the probability that FinTechX will grow by more than 20% in the next 1 year?",
            min_value=0,
            max_value=100,
            value=50,
            key="q1",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 2</div>', unsafe_allow_html=True)
        q2 = st.radio(
            "FinTechX's CEO is an experienced executive with a Trendyol background. Based on this, what is your first impression of the company's future performance?",
            ["Successful", "Moderate", "Unsuccessful", "I cannot decide with this information"],
            key="q2",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 3</div>', unsafe_allow_html=True)
        q3 = st.slider(
            "FinTechX grew by 15% last year. What is your growth estimate for this year?",
            min_value=0,
            max_value=100,
            value=15,
            key="q3",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 4</div>', unsafe_allow_html=True)
        q4 = st.slider(
            "During this period, fintech failures are frequently discussed in the media. What do you think is the probability that FinTechX will fail?",
            min_value=0,
            max_value=100,
            value=25,
            key="q4",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 5</div>', unsafe_allow_html=True)
        q5 = st.radio(
            '"If I can regularly access FinTechX\'s financial statements, I believe I can control my risk."',
            ["Strongly agree", "Agree", "Undecided", "Disagree", "Strongly disagree"],
            key="q5",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 6</div>', unsafe_allow_html=True)
        q6 = st.radio(
            'CFO: "The company is doing well." Audit report: "Cash flow is risky." Which source do you trust more?',
            ["CFO", "Audit report", "Undecided"],
            key="q6",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 7A</div>', unsafe_allow_html=True)
        q7a = st.text_area(
            "If you personally lost money, why do you think it happened?",
            placeholder="Write a short explanation in English...",
            height=120,
            key="q7a",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 7B</div>', unsafe_allow_html=True)
        q7b = st.text_area(
            "If your friend lost money, why do you think it happened?",
            placeholder="Write a short explanation in English...",
            height=120,
            key="q7b",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown('<div class="question-badge">Question 8</div>', unsafe_allow_html=True)
        q8 = st.radio(
            "FinTechX failed. Was this outcome easy to predict?",
            ["Yes, it was obvious", "No, it was not obvious", "Not sure"],
            key="q8",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        submit_clicked = st.form_submit_button("Finish game and submit")

    if submit_clicked:
        if remaining_seconds <= 0:
            mark_timeout(player_name, int(time.time() - st.session_state.start_ts))
            st.error("Submission was not accepted because the time limit expired.")
        elif not q7a.strip() or not q7b.strip():
            st.error("Please answer both Question 7A and Question 7B before submitting.")
        else:
            responses = {
                "Q1": q1,
                "Q2": q2,
                "Q3": q3,
                "Q4": q4,
                "Q5": q5,
                "Q6": q6,
                "Q7a": q7a,
                "Q7b": q7b,
                "Q8": q8,
            }
            result_payload = build_result_payload(responses)
            final_elapsed = int(time.time() - st.session_state.start_ts)
            finish_player(player_name, result_payload["score"], final_elapsed)
            st.session_state.game_submitted = True
            st.session_state.result_payload = {
                **result_payload,
                "responses": responses,
                "elapsed_seconds": final_elapsed,
            }
            st.rerun()


# -----------------------------
# Results
# -----------------------------
if st.session_state.game_submitted and st.session_state.result_payload:
    result_payload = st.session_state.result_payload
    responses = result_payload["responses"]
    elapsed = result_payload["elapsed_seconds"]

    st.write("")
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Game finished</div>
            <div class="section-sub">Your result has been saved to the shared leaderboard.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    score_col, time_col, rank_col = st.columns(3)
    leaderboard_rows = get_leaderboard_rows()
    player_rank = next((row["Rank"] for row in leaderboard_rows if row["Name"] == player_name), "—")

    with score_col:
        st.metric("Your score", f"{result_payload['score']} / 96")
    with time_col:
        st.metric("Your time", format_seconds(elapsed))
    with rank_col:
        st.metric("Your rank", str(player_rank))

    st.subheader("Your bias-awareness breakdown")
    for item in result_payload["breakdown"]:
        points = item["Points"]
        css = "result-good" if points >= 10 else "result-warn" if points >= 6 else "result-bad"
        st.markdown(
            f"""
            <div class="glass-card {css}" style="margin-bottom:0.8rem;">
                <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;">
                    <div>
                        <div style="font-size:0.84rem;color:#9fb0d0;">{item['Question']} • {item['Bias']}</div>
                        <div style="font-size:1.05rem;font-weight:800;margin-top:0.2rem;">{item['Signal']}</div>
                        <div style="margin-top:0.35rem;color:#dce7fb;">{item['Explanation']}</div>
                    </div>
                    <div style="font-size:1.1rem;font-weight:800;white-space:nowrap;">{points} pts</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("See your submitted answers", expanded=False):
        st.markdown(
            f"""
            - **Q1:** {responses['Q1']}%
            - **Q2:** {responses['Q2']}
            - **Q3:** {responses['Q3']}%
            - **Q4:** {responses['Q4']}%
            - **Q5:** {responses['Q5']}
            - **Q6:** {responses['Q6']}
            - **Q7A:** {responses['Q7a']}
            - **Q7B:** {responses['Q7b']}
            - **Q8:** {responses['Q8']}
            """
        )

    summary_lines = [
        "Question,Response",
        f'Q1,"{responses["Q1"]}%"',
        f'Q2,"{responses["Q2"]}"',
        f'Q3,"{responses["Q3"]}%"',
        f'Q4,"{responses["Q4"]}%"',
        f'Q5,"{responses["Q5"]}"',
        f'Q6,"{responses["Q6"]}"',
        f'Q7A,"{responses["Q7a"].replace(chr(34), chr(39))}"',
        f'Q7B,"{responses["Q7b"].replace(chr(34), chr(39))}"',
        f'Q8,"{responses["Q8"]}"',
        f'Score,"{result_payload["score"]}"',
        f'Time,"{format_seconds(elapsed)}"',
    ]
    csv_text = "\n".join(summary_lines)
    st.download_button(
        "Download your result as CSV",
        data=csv_text,
        file_name=f"fintechx_{player_name.lower().replace(' ', '_')}_result.csv",
        mime="text/csv",
    )


# -----------------------------
# Shared ranking table
# -----------------------------
st.divider()
st.subheader("Final ranking table")
leaderboard_rows = get_leaderboard_rows()
if leaderboard_rows:
    st.dataframe(leaderboard_rows, use_container_width=True, hide_index=True)
else:
    st.info("No finished players yet.")


# -----------------------------
# Teaching content
# -----------------------------
with st.expander("Bias explanations for classroom discussion", expanded=False):
    for title, details in BIAS_DETAILS.items():
        st.markdown(f"### {title}")
        st.markdown(f"**Observation:** {details['observation']}")
        st.markdown(f"**Why this is a bias:** {details['why']}")
        st.markdown("**Possible impact on financial decisions**")
        for item in details["impact"]:
            st.markdown(f"- {item}")
        st.markdown("**Discussion questions**")
        for item in details["discussion"]:
            st.markdown(f"- {item}")
        st.markdown("---")

st.markdown(
    "<div class='footer-note'>Instructor note: The ranking is a classroom gamification layer. It rewards answers that better resist common behavioral biases, but it does not prove that a student is unbiased in real life.</div>",
    unsafe_allow_html=True,
)
