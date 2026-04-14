import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


st.set_page_config(
    page_title="FinTechX Bias Challenge",
    page_icon="📈",
    layout="wide",
)

MAX_DURATION = 5 * 60
DATA_PATH = Path("/mnt/data/fintechx_game_state.json")
ACTIVE_TTL_SECONDS = 30 * 60


QUESTIONS: List[Dict[str, object]] = [
    {
        "id": "q1",
        "label": "Question 1",
        "bias": "Overconfidence Bias",
        "story": (
            "You have joined a student investment committee that is reviewing FinTechX, a fast-growing digital "
            "payments startup. The company has added merchants quickly, app activity has been rising, and the mood "
            "in the room is highly optimistic. Several participants are already speaking as if strong growth next "
            "year is almost a given, even though no full valuation model has been shown yet. Before any deeper data "
            "arrives, you are asked to make a one-year judgment call."
        ),
        "prompt": "What probability would you assign to FinTechX growing by more than 20% in the next 12 months?",
        "options": ["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"],
    },
    {
        "id": "q2",
        "label": "Question 2",
        "bias": "Representativeness Bias",
        "story": (
            "Before you see revenue quality, margins, or cash flow, the moderator gives one striking detail: "
            "FinTechX's CEO previously held a senior role at Trendyol and is known for scaling digital products. "
            "The room reacts immediately. Some people begin to treat that biography as if it already proves the "
            "company's future. You must give your first impression while knowing that the only concrete fact so far "
            "is the CEO's impressive background."
        ),
        "prompt": "Based only on that information, what is your first impression of FinTechX's future performance?",
        "options": [
            "Successful",
            "Moderate",
            "Unsuccessful",
            "I cannot decide from this information alone",
        ],
    },
    {
        "id": "q3",
        "label": "Question 3",
        "bias": "Anchoring Bias",
        "story": (
            "The committee now reveals one simple number: FinTechX grew by 15% last year. You are not shown new "
            "guidance, competitor benchmarks, or any macroeconomic assumptions. Even so, that 15% figure becomes "
            "the number everyone repeats first. Some participants begin adjusting only slightly up or down from it. "
            "You have to make your forecast before any other reference point is introduced."
        ),
        "prompt": "What is your estimate for FinTechX's growth this year?",
        "options": ["0-10%", "11-15%", "16-20%", "21-30%", "Above 30%"],
    },
    {
        "id": "q4",
        "label": "Question 4",
        "bias": "Availability Bias",
        "story": (
            "For the last two weeks, the financial media has been full of fintech bankruptcy stories, failed funding "
            "rounds, layoffs, and sharp market commentary about the sector. When FinTechX appears on screen, those "
            "recent headlines are still fresh in everyone's memory. However, you are not given any direct evidence "
            "that FinTechX itself is facing a special solvency problem. You still need to estimate the chance that "
            "the company could fail."
        ),
        "prompt": "What probability would you assign to FinTechX failing under these conditions?",
        "options": ["0-10%", "11-25%", "26-40%", "41-60%", "Above 60%"],
    },
    {
        "id": "q5",
        "label": "Question 5",
        "bias": "Illusion of Control",
        "story": (
            "Imagine that, as an investor, you will receive regular access to FinTechX's financial statements every "
            "quarter. That sounds reassuring, and several people in the room start to feel that close monitoring would "
            "make the investment much safer. Yet even with frequent statements, the company would still face "
            "competition, regulation, execution risk, and macroeconomic shocks. You now need to react to a statement "
            "about control and risk."
        ),
        "prompt": "How strongly do you agree with the following statement? 'If I can regularly access FinTechX's financial statements, I can control my risk.'",
        "options": [
            "Strongly agree",
            "Agree",
            "Undecided",
            "Disagree",
            "Strongly disagree",
        ],
    },
    {
        "id": "q6",
        "label": "Question 6",
        "bias": "Cognitive Conflict",
        "story": (
            "Two signals arrive at the same time. In a presentation, the CFO says the business is doing well, demand "
            "remains strong, and management feels confident. A separate audit note, however, warns that the company's "
            "cash flow position is fragile and could become risky if conditions tighten. One message is optimistic and "
            "human; the other is colder, more formal, and harder to accept. You must decide which source deserves more trust."
        ),
        "prompt": "Which source would you trust more in this situation?",
        "options": ["The CFO", "The audit report", "I need more evidence before choosing"],
    },
    {
        "id": "q7a",
        "label": "Question 7A",
        "bias": "Attribution / Self-Serving Bias",
        "story": (
            "Imagine that you personally invested in FinTechX and later lost money. When people reflect on their own "
            "losses, they often protect their self-image by blaming the market, timing, or luck more than their own "
            "decisions. Your answer does not need to be morally perfect; choose the explanation that feels closest to "
            "your first instinct about your own loss."
        ),
        "prompt": "If you lost money yourself, which explanation feels closest to your first instinct?",
        "options": [
            "Mainly market conditions and bad timing",
            "Mostly my own decision mistakes",
            "A mix of market conditions and my own decisions",
            "Just bad luck",
        ],
    },
    {
        "id": "q7b",
        "label": "Question 7B",
        "bias": "Attribution / Self-Serving Bias",
        "story": (
            "Now imagine that the exact same loss happened to a friend instead of you. In finance, people often judge "
            "others more harshly than themselves and become quicker to say the other person made avoidable mistakes. "
            "Again, choose the explanation that feels closest to your first instinct rather than the most socially "
            "acceptable answer."
        ),
        "prompt": "If your friend lost money, which explanation feels closest to your first instinct?",
        "options": [
            "Mainly market conditions and bad timing",
            "Mostly my friend's decision mistakes",
            "A mix of market conditions and my friend's decisions",
            "Just bad luck",
        ],
    },
    {
        "id": "q8",
        "label": "Question 8",
        "bias": "Hindsight Bias",
        "story": (
            "Months later, FinTechX has failed. Funding dried up, performance weakened, and the company could not keep "
            "operating. Once the ending is known, the whole story starts to look cleaner and more predictable than it "
            "felt before the collapse. You are asked to judge the past after already knowing the result, which is where "
            "many investors become overconfident about what they supposedly 'knew all along.'"
        ),
        "prompt": "Looking back after the failure, does this outcome feel easy to predict?",
        "options": ["Yes, it was obvious", "No, it was not obvious", "Not sure"],
    },
]


BIAS_LIBRARY: Dict[str, Dict[str, object]] = {
    "Overconfidence Bias": {
        "observation": "Many students choose high confidence ranges such as 61-80% or even 81-100%.",
        "why": "People often overestimate their forecasting skill, market-reading ability, and personal judgment.",
        "impact": [
            "Taking too much risk",
            "Trading too often",
            "Holding losing positions too long",
            "Under-diversification",
        ],
        "discussion": [
            "What made the forecast feel so certain?",
            "How hard is a one-year growth prediction in real markets?",
            "How can overconfidence damage portfolio decisions?",
        ],
    },
    "Representativeness Bias": {
        "observation": "Students often infer that a strong executive profile automatically means a strong company outcome.",
        "why": "The brain uses a shortcut: good story, good company. That feels convincing even when data is missing.",
        "impact": [
            "Investing in narratives instead of evidence",
            "Overtrusting charismatic leaders",
            "Opening positions with limited data",
        ],
        "discussion": [
            "Why is a CEO story so persuasive?",
            "What key data was still missing?",
            "Do real investors also buy stories too easily?",
        ],
    },
    "Anchoring Bias": {
        "observation": "Answers often stay close to the 15% reference point that appeared first.",
        "why": "The first number becomes a mental anchor, and people usually adjust away from it too little.",
        "impact": [
            "Slow adaptation to new information",
            "Target prices clustering too closely",
            "Reluctance to rebalance portfolios",
        ],
        "discussion": [
            "Did the 15% figure pull your answer toward it?",
            "Would your forecast change if last year's number had been 40% instead?",
            "Why are first numbers so sticky in finance?",
        ],
    },
    "Availability Bias": {
        "observation": "Fresh negative news often pushes failure estimates higher, even without company-specific evidence.",
        "why": "The mind treats recent, vivid, easy-to-recall information as more probable than it really is.",
        "impact": [
            "Panic selling",
            "Exaggerated risk perception",
            "Overreacting to media sentiment",
        ],
        "discussion": [
            "What headlines came to mind while answering?",
            "Would your estimate look different without those headlines?",
            "How can investors defend themselves from media-driven judgments?",
        ],
    },
    "Illusion of Control": {
        "observation": "Many students agree that more information means more control over risk.",
        "why": "People often confuse being informed with being in control, even though many risks stay outside investor influence.",
        "impact": [
            "Position sizes that are too large",
            "Risk management mistakes",
            "Overconfidence in complex assets",
        ],
        "discussion": [
            "What is the difference between information and control?",
            "What risks remain even with strong reporting access?",
            "Why do investors still crave the feeling of control?",
        ],
    },
    "Cognitive Conflict": {
        "observation": "Optimistic management commentary often feels easier to accept than a difficult audit warning.",
        "why": "When information conflicts, the brain prefers the message that is simpler, warmer, or emotionally easier.",
        "impact": [
            "Ignoring bad news",
            "Excessive optimism",
            "Underestimating formal risk signals",
        ],
        "discussion": [
            "Why does the CFO message feel more comfortable?",
            "Why can formal warnings be easier to dismiss?",
            "How do professionals stay rational under conflicting signals?",
        ],
    },
    "Attribution / Self-Serving Bias": {
        "observation": "People often blame outside conditions for their own losses but personal mistakes for someone else's.",
        "why": "The mind protects self-image by shifting blame away from the self while judging others more harshly.",
        "impact": [
            "Learning less from mistakes",
            "Distorted performance review",
            "Weaker accountability",
        ],
        "discussion": [
            "Did you apply the same standard to yourself and your friend?",
            "Why is self-criticism harder under loss?",
            "How might this bias affect fund managers?",
        ],
    },
    "Hindsight Bias": {
        "observation": "After failure happens, many people say the warning signs had been obvious all along.",
        "why": "Once the outcome is known, the brain rewrites the past and makes uncertainty look smaller than it was.",
        "impact": [
            "Stronger overconfidence",
            "The illusion of 'I knew it'",
            "Poorer future risk analysis",
        ],
        "discussion": [
            "Was the failure really obvious before it happened?",
            "Why does certainty grow after the event?",
            "How can hindsight distort investor learning?",
        ],
    },
}


SCORING_MAP = {
    "q1": {"0-20%": 3, "21-40%": 5, "41-60%": 3, "61-80%": 1, "81-100%": 0},
    "q2": {
        "Successful": 1,
        "Moderate": 3,
        "Unsuccessful": 2,
        "I cannot decide from this information alone": 5,
    },
    "q3": {"0-10%": 4, "11-15%": 1, "16-20%": 1, "21-30%": 4, "Above 30%": 3},
    "q4": {"0-10%": 5, "11-25%": 4, "26-40%": 2, "41-60%": 1, "Above 60%": 0},
    "q5": {
        "Strongly agree": 0,
        "Agree": 1,
        "Undecided": 3,
        "Disagree": 4,
        "Strongly disagree": 5,
    },
    "q6": {"The CFO": 1, "The audit report": 5, "I need more evidence before choosing": 4},
    "q8": {"Yes, it was obvious": 0, "No, it was not obvious": 5, "Not sure": 3},
}

MAX_SCORE = 40


ANSWER_NOTES = {
    "q1": {
        "0-20%": ("Cautious forecast", "You resisted the urge to sound highly certain in a very uncertain one-year prediction."),
        "21-40%": ("Most calibrated range", "This range reflects caution without pretending the outcome is either impossible or highly predictable."),
        "41-60%": ("Moderate confidence", "Your answer still gives a fairly strong forecast, which may reflect some confidence in your own judgment."),
        "61-80%": ("Strong overconfidence signal", "A high-confidence range suggests that the future may feel easier to forecast than it really is."),
        "81-100%": ("Very strong overconfidence signal", "Extremely high certainty is rare in real investing and often reveals overconfidence."),
    },
    "q2": {
        "Successful": ("Representativeness signal", "You may be projecting the CEO's strong background directly onto the company's future."),
        "Moderate": ("Mild narrative pull", "You did not fully buy the story, but the CEO background may still have shaped your first impression."),
        "Unsuccessful": ("Counter-narrative reaction", "You pushed back against the positive story, though this is still a judgment with little data."),
        "I cannot decide from this information alone": ("Data-aware response", "You resisted turning one attractive fact into a full company forecast."),
    },
    "q3": {
        "0-10%": ("Lower anchoring signal", "You moved clearly away from the 15% reference point."),
        "11-15%": ("Anchoring signal", "Your answer stayed very close to the initial number that was placed in front of you."),
        "16-20%": ("Anchoring signal", "Your forecast still hugs the original 15% reference point."),
        "21-30%": ("Lower anchoring signal", "You adjusted away from the original figure more decisively."),
        "Above 30%": ("Lower anchoring signal", "You did not let the first number fully control your estimate."),
    },
    "q4": {
        "0-10%": ("Lower availability signal", "You did not let recent headlines dominate your estimate."),
        "11-25%": ("Mild availability signal", "You stayed fairly measured despite the recent media noise."),
        "26-40%": ("Moderate availability signal", "Recent bad news may have made failure feel more likely than the available evidence supports."),
        "41-60%": ("Strong availability signal", "Fresh negative examples seem to have pulled your judgment upward."),
        "Above 60%": ("Very strong availability signal", "This answer suggests recent headlines may be overwhelming company-specific analysis."),
    },
    "q5": {
        "Strongly agree": ("Strong illusion of control signal", "You appear to treat information access as if it creates control over risk."),
        "Agree": ("Illusion of control signal", "You may be confusing good monitoring with actual control of uncertain outcomes."),
        "Undecided": ("Balanced tension", "You seem to recognize that information helps, but does not remove uncertainty."),
        "Disagree": ("Lower illusion of control signal", "You distinguish between being informed and being in control."),
        "Strongly disagree": ("Strong bias resistance", "You clearly separate information access from true control over risk."),
    },
    "q6": {
        "The CFO": ("Cognitive conflict signal", "You favored the more optimistic and human message over the tougher formal warning."),
        "The audit report": ("Analytical response", "You gave more weight to the formal risk signal despite its discomfort."),
        "I need more evidence before choosing": ("Measured response", "You did not rush to resolve the tension with a simplistic answer."),
    },
    "q8": {
        "Yes, it was obvious": ("Hindsight bias signal", "Knowing the ending can make the past feel more predictable than it actually was."),
        "No, it was not obvious": ("Lower hindsight signal", "You preserved the uncertainty that existed before the failure happened."),
        "Not sure": ("Partial hindsight resistance", "You noticed that hindsight makes judgment harder, even if the outcome now feels explainable."),
    },
}


CSS = """
<style>
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #111827 100%);
        padding: 1.35rem 1.5rem;
        border-radius: 24px;
        color: white;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 40px rgba(15,23,42,0.28);
        margin-bottom: 1rem;
    }
    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.8rem;
    }
    .chip {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        padding: 0.45rem 0.75rem;
        border-radius: 999px;
        font-size: 0.92rem;
    }
    .card {
        background: #ffffff;
        border-radius: 22px;
        padding: 1.25rem 1.25rem 1rem 1.25rem;
        border: 1px solid rgba(15,23,42,0.08);
        box-shadow: 0 12px 30px rgba(15,23,42,0.08);
        margin-bottom: 1rem;
    }
    .soft-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 20px;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(15,23,42,0.08);
        box-shadow: 0 8px 20px rgba(15,23,42,0.05);
        margin-bottom: 0.85rem;
    }
    .metric {
        background: #0f172a;
        color: white;
        border-radius: 18px;
        padding: 0.9rem 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .metric .label {
        font-size: 0.85rem;
        opacity: 0.78;
        margin-bottom: 0.2rem;
    }
    .metric .value {
        font-size: 1.45rem;
        font-weight: 700;
    }
    .story-box {
        background: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 1rem 1rem 1rem 1rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        color: #0f172a;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
        color: #0f172a;
    }
    .tiny-note {
        color: #475569;
        font-size: 0.92rem;
    }
</style>
"""


# -----------------------------
# Storage helpers
# -----------------------------

def default_data() -> Dict[str, object]:
    return {"leaderboard": {}, "active": {}}


class LockedFile:
    def __init__(self, path: Path, mode: str):
        self.path = path
        self.mode = mode
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = open(self.path, self.mode, encoding="utf-8")
        if fcntl is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
        return self.handle

    def __exit__(self, exc_type, exc, tb):
        if self.handle and fcntl is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        if self.handle:
            self.handle.close()



def load_data() -> Dict[str, object]:
    if not DATA_PATH.exists():
        save_data(default_data())
    with LockedFile(DATA_PATH, "r") as f:
        raw = f.read().strip()
        if not raw:
            return default_data()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return default_data()
    data.setdefault("leaderboard", {})
    data.setdefault("active", {})
    return data



def save_data(data: Dict[str, object]) -> None:
    tmp_path = DATA_PATH.with_suffix(".tmp")
    with LockedFile(tmp_path, "w") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, DATA_PATH)



def normalize_name(name: str) -> str:
    return " ".join(name.strip().lower().split())



def cleanup_active(data: Dict[str, object]) -> Dict[str, object]:
    now = time.time()
    active = data.get("active", {})
    data["active"] = {
        key: value
        for key, value in active.items()
        if now - float(value.get("heartbeat", value.get("started_at", now))) <= ACTIVE_TTL_SECONDS
    }
    return data



def touch_active(name: str) -> None:
    if not name:
        return
    data = cleanup_active(load_data())
    key = normalize_name(name)
    data["active"][key] = {
        "name": name.strip(),
        "started_at": st.session_state.get("started_at", time.time()),
        "heartbeat": time.time(),
    }
    save_data(data)



def remove_active(name: str) -> None:
    if not name:
        return
    data = cleanup_active(load_data())
    data.get("active", {}).pop(normalize_name(name), None)
    save_data(data)



def update_leaderboard(name: str, score: int, elapsed_seconds: int) -> str:
    data = cleanup_active(load_data())
    key = normalize_name(name)
    existing = data["leaderboard"].get(key)
    result_status = "New entry"
    candidate = {
        "name": name.strip(),
        "score": int(score),
        "time_sec": int(elapsed_seconds),
        "max_score": MAX_SCORE,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    if existing is None:
        data["leaderboard"][key] = candidate
    else:
        old_score = int(existing.get("score", 0))
        old_time = int(existing.get("time_sec", 999999))
        if score > old_score or (score == old_score and elapsed_seconds < old_time):
            data["leaderboard"][key] = candidate
            result_status = "Best score updated"
        else:
            result_status = "Previous best kept"
    data.get("active", {}).pop(key, None)
    save_data(data)
    return result_status



def get_scoreboard_df() -> pd.DataFrame:
    data = cleanup_active(load_data())
    save_data(data)
    items = list(data.get("leaderboard", {}).values())
    if not items:
        return pd.DataFrame(columns=["Rank", "Name", "Score", "Bias Resistance %", "Time"])
    items.sort(key=lambda x: (-int(x.get("score", 0)), int(x.get("time_sec", 999999)), x.get("name", "")))
    rows = []
    for idx, item in enumerate(items, start=1):
        score = int(item.get("score", 0))
        rows.append(
            {
                "Rank": idx,
                "Name": item.get("name", ""),
                "Score": f"{score}/{MAX_SCORE}",
                "Bias Resistance %": f"{round(score / MAX_SCORE * 100)}%",
                "Time": format_seconds(int(item.get("time_sec", 0))),
            }
        )
    return pd.DataFrame(rows)



def get_visible_names() -> Tuple[List[str], List[str]]:
    data = cleanup_active(load_data())
    save_data(data)
    active_names = sorted({v.get("name", "") for v in data.get("active", {}).values() if v.get("name")})
    completed_names = sorted({v.get("name", "") for v in data.get("leaderboard", {}).values() if v.get("name")})
    return active_names, completed_names


# -----------------------------
# Game helpers
# -----------------------------

def init_state() -> None:
    st.session_state.setdefault("player_name", "")
    st.session_state.setdefault("started", False)
    st.session_state.setdefault("started_at", None)
    st.session_state.setdefault("current_index", 0)
    st.session_state.setdefault("submitted", False)
    st.session_state.setdefault("answers", {})
    st.session_state.setdefault("score", None)
    st.session_state.setdefault("elapsed_seconds", 0)
    st.session_state.setdefault("result_status", "")
    st.session_state.setdefault("timed_out", False)



def reset_game(keep_name: bool = True) -> None:
    name = st.session_state.get("player_name", "") if keep_name else ""
    keys_to_remove = [k for k in list(st.session_state.keys()) if k.startswith("radio_")]
    for key in keys_to_remove:
        st.session_state.pop(key, None)
    st.session_state["started"] = False
    st.session_state["started_at"] = None
    st.session_state["current_index"] = 0
    st.session_state["submitted"] = False
    st.session_state["answers"] = {}
    st.session_state["score"] = None
    st.session_state["elapsed_seconds"] = 0
    st.session_state["result_status"] = ""
    st.session_state["timed_out"] = False
    st.session_state["player_name"] = name
    if name:
        remove_active(name)



def format_seconds(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"



def current_elapsed_seconds() -> int:
    started_at = st.session_state.get("started_at")
    if not started_at:
        return 0
    return int(time.time() - float(started_at))



def collect_answers_from_widgets() -> Dict[str, str]:
    answers = dict(st.session_state.get("answers", {}))
    for q in QUESTIONS:
        widget_key = f"radio_{q['id']}"
        value = st.session_state.get(widget_key)
        if value:
            answers[q["id"]] = value
    st.session_state["answers"] = answers
    return answers



def score_q7(q7a: str, q7b: str) -> Tuple[int, str, str]:
    self_external = q7a in {"Mainly market conditions and bad timing", "Just bad luck"}
    self_internal = q7a == "Mostly my own decision mistakes"
    self_mixed = q7a == "A mix of market conditions and my own decisions"

    friend_external = q7b in {"Mainly market conditions and bad timing", "Just bad luck"}
    friend_internal = q7b == "Mostly my friend's decision mistakes"
    friend_mixed = q7b == "A mix of market conditions and my friend's decisions"

    if self_external and friend_internal:
        return 0, "Strong self-serving bias signal", "You protected yourself with outside explanations while judging your friend more personally."
    if self_mixed and friend_mixed:
        return 5, "Balanced attribution", "You applied the same mixed standard to both people, which reduces self-serving bias."
    if self_internal and friend_internal:
        return 4, "Consistent accountability", "You used the same personal-responsibility standard for both cases."
    if self_external and friend_mixed:
        return 2, "Mild self-serving pattern", "You were softer on yourself than on your friend, though not in the most extreme way."
    if self_mixed and friend_internal:
        return 2, "Harsh-on-others pattern", "You were somewhat tougher on your friend than on yourself."
    if self_internal and friend_external:
        return 3, "Reverse asymmetry", "You were harder on yourself than on your friend, which is unusual but still asymmetric."
    return 3, "Mixed attribution pattern", "Your answers do not show the classic pattern strongly, but they are not perfectly balanced either."



def calculate_score(answers: Dict[str, str]) -> Tuple[int, Dict[str, Tuple[str, str]]]:
    total = 0
    notes: Dict[str, Tuple[str, str]] = {}

    for qid, mapping in SCORING_MAP.items():
        answer = answers.get(qid)
        if answer:
            total += int(mapping.get(answer, 0))
            notes[qid] = ANSWER_NOTES[qid][answer]

    q7a = answers.get("q7a")
    q7b = answers.get("q7b")
    if q7a and q7b:
        q7_score, q7_title, q7_text = score_q7(q7a, q7b)
        total += q7_score
        notes["q7"] = (q7_title, q7_text)
    else:
        notes["q7"] = ("Incomplete attribution pattern", "One or both attribution questions were left unanswered before time ran out.")

    return total, notes



def finalize_submission(force_timeout: bool = False) -> None:
    answers = collect_answers_from_widgets()
    elapsed = min(current_elapsed_seconds(), MAX_DURATION)
    score, notes = calculate_score(answers)

    st.session_state["submitted"] = True
    st.session_state["timed_out"] = force_timeout
    st.session_state["score"] = score
    st.session_state["elapsed_seconds"] = elapsed
    st.session_state["answer_notes"] = notes
    st.session_state["answers"] = answers
    st.session_state["result_status"] = update_leaderboard(st.session_state["player_name"], score, elapsed)



def answer_progress(answers: Dict[str, str]) -> int:
    count = 0
    for q in QUESTIONS:
        if answers.get(q["id"]):
            count += 1
    return count



def render_metric(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def sidebar_status() -> None:
    active_names, completed_names = get_visible_names()
    board_df = get_scoreboard_df()

    with st.sidebar:
        st.markdown("## Live room")
        st.caption("Everyone can see participant names and the best leaderboard so far.")

        st.markdown("### Active players")
        if active_names:
            for name in active_names:
                st.markdown(f"- {name}")
        else:
            st.caption("No one is currently answering.")

        st.markdown("### Completed players")
        if completed_names:
            for name in completed_names:
                st.markdown(f"- {name}")
        else:
            st.caption("No completed runs yet.")

        st.markdown("### Top leaderboard")
        if board_df.empty:
            st.caption("The leaderboard will appear after the first submission.")
        else:
            st.dataframe(board_df.head(10), use_container_width=True, hide_index=True)



def render_home() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1 style="margin:0;">FinTechX Bias Challenge</h1>
            <p style="margin:0.55rem 0 0 0; font-size:1.02rem; opacity:0.92;">
                A fast classroom game about behavioral finance. One story appears at a time, all answers are multiple choice,
                and you have only five minutes to finish.
            </p>
            <div class="chip-row">
                <div class="chip">English only</div>
                <div class="chip">1 question per screen</div>
                <div class="chip">5-minute timer</div>
                <div class="chip">Final leaderboard</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Enter the game")
        st.write(
            "Use your name exactly as you want it to appear to everyone. When you start, your name enters the live room list immediately."
        )
        name = st.text_input("Your name", value=st.session_state.get("player_name", ""), placeholder="For example: Ayse Kaya")
        st.session_state["player_name"] = name
        st.caption("Your best score is kept if you play again with the same name.")
        start_disabled = not name.strip()
        if st.button("Start challenge", type="primary", use_container_width=True, disabled=start_disabled):
            reset_game(keep_name=True)
            st.session_state["player_name"] = name.strip()
            st.session_state["started"] = True
            st.session_state["started_at"] = time.time()
            st.session_state["current_index"] = 0
            touch_active(name.strip())
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown("### Game rules")
        st.markdown(
            """
            - You will see one scenario at a time.
            - Every question is multiple choice.
            - The timer stops at **5:00**.
            - Unanswered questions after time runs out count as zero.
            - Final ranking is based on **score first**, then **faster time**.
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown("### What the score means")
        st.write(
            "This is a classroom indicator of bias resistance, not a diagnosis. Higher scores suggest more cautious, data-aware, and less reflexive decisions under uncertainty."
        )
        st.markdown('</div>', unsafe_allow_html=True)



def render_question_screen() -> None:
    st_autorefresh(interval=1000, key="game_timer_refresh")

    elapsed = current_elapsed_seconds()
    remaining = MAX_DURATION - elapsed
    st.session_state["elapsed_seconds"] = max(0, min(elapsed, MAX_DURATION))
    touch_active(st.session_state.get("player_name", ""))

    if remaining <= 0:
        finalize_submission(force_timeout=True)
        st.rerun()

    answers = collect_answers_from_widgets()
    current_index = st.session_state.get("current_index", 0)
    current_index = min(max(current_index, 0), len(QUESTIONS) - 1)
    q = QUESTIONS[current_index]
    widget_key = f"radio_{q['id']}"

    st.markdown(
        f"""
        <div class="hero">
            <h2 style="margin:0;">{q['label']} · {q['bias']}</h2>
            <p style="margin:0.5rem 0 0 0; opacity:0.92;">{st.session_state['player_name']}, read the scenario and choose one answer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric("Time left", format_seconds(remaining))
    with m2:
        render_metric("Progress", f"{current_index + 1}/{len(QUESTIONS)}")
    with m3:
        render_metric("Answered", f"{answer_progress(answers)}/{len(QUESTIONS)}")

    st.progress((current_index + 1) / len(QUESTIONS))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Scenario</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="story-box">{q["story"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**Decision prompt:** {q['prompt']}")
    st.caption("Choose one option before moving on.")

    st.radio(
        "Answer",
        q["options"],
        index=None,
        key=widget_key,
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    prev_col, next_col = st.columns([1, 1])
    with prev_col:
        if st.button("← Previous", use_container_width=True, disabled=current_index == 0):
            st.session_state["current_index"] = max(0, current_index - 1)
            st.rerun()
    with next_col:
        is_last = current_index == len(QUESTIONS) - 1
        button_label = "Finish and submit" if is_last else "Next →"
        if st.button(button_label, type="primary", use_container_width=True):
            selected = st.session_state.get(widget_key)
            if not selected:
                st.warning("Please choose one option before continuing.")
            else:
                collect_answers_from_widgets()
                if is_last:
                    finalize_submission(force_timeout=False)
                else:
                    st.session_state["current_index"] = current_index + 1
                st.rerun()



def render_results() -> None:
    score = int(st.session_state.get("score", 0) or 0)
    elapsed = int(st.session_state.get("elapsed_seconds", 0) or 0)
    notes = st.session_state.get("answer_notes", {})
    answers = st.session_state.get("answers", {})
    percent = round(score / MAX_SCORE * 100)

    banner_text = "Time is up. Your current answers were submitted automatically." if st.session_state.get("timed_out") else "Your run has been submitted successfully."
    banner_type = st.warning if st.session_state.get("timed_out") else st.success
    banner_type(f"{banner_text} {st.session_state.get('result_status', '')}")

    st.markdown(
        f"""
        <div class="hero">
            <h1 style="margin:0;">Results for {st.session_state['player_name']}</h1>
            <p style="margin:0.55rem 0 0 0; opacity:0.92;">Your bias-resistance score rewards more cautious, evidence-aware decisions under pressure.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric("Score", f"{score}/{MAX_SCORE}")
    with c2:
        render_metric("Bias resistance", f"{percent}%")
    with c3:
        render_metric("Completion time", format_seconds(elapsed))

    st.markdown("### Your bias profile")
    bias_order = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8"]
    for key in bias_order:
        if key == "q7":
            title = "Question 7A + 7B · Attribution / Self-Serving Bias"
            choice_text = f"You: {answers.get('q7a', 'No answer')} · Friend: {answers.get('q7b', 'No answer')}"
        else:
            q = next(item for item in QUESTIONS if item["id"] == key)
            title = f"{q['label']} · {q['bias']}"
            choice_text = answers.get(key, "No answer")
        note_title, note_text = notes.get(key, ("No interpretation yet", "No answer recorded for this section."))
        st.markdown(
            f"""
            <div class="soft-card">
                <div class="section-title">{title}</div>
                <div class="tiny-note" style="margin-bottom:0.45rem;"><strong>Your choice:</strong> {choice_text}</div>
                <div><strong>{note_title}</strong></div>
                <div class="tiny-note">{note_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Full leaderboard")
    board_df = get_scoreboard_df()
    if board_df.empty:
        st.info("No leaderboard entries yet.")
    else:
        st.dataframe(board_df, use_container_width=True, hide_index=True)

    st.markdown("### Bias explanations for class discussion")
    used_biases = []
    for q in QUESTIONS:
        bias = q["bias"]
        if bias not in used_biases:
            used_biases.append(bias)
    for bias in used_biases:
        details = BIAS_LIBRARY[bias]
        with st.expander(bias, expanded=False):
            st.markdown(f"**Observation**  \\n{details['observation']}")
            st.markdown(f"**Why this bias happens**  \\n{details['why']}")
            st.markdown("**Possible financial impact**")
            for item in details["impact"]:
                st.markdown(f"- {item}")
            st.markdown("**Discussion questions**")
            for item in details["discussion"]:
                st.markdown(f"- {item}")

    if st.button("Play again with the same name", use_container_width=True):
        reset_game(keep_name=True)
        st.session_state["started"] = True
        st.session_state["started_at"] = time.time()
        st.session_state["current_index"] = 0
        touch_active(st.session_state["player_name"])
        st.rerun()


# -----------------------------
# App
# -----------------------------

st.markdown(CSS, unsafe_allow_html=True)
init_state()
sidebar_status()

if st.session_state.get("submitted"):
    render_results()
elif st.session_state.get("started"):
    render_question_screen()
else:
    render_home()
