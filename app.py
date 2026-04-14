import re
from typing import Dict, List, Tuple

import streamlit as st


st.set_page_config(
    page_title="FinTechX Behavioral Biases App",
    page_icon="📊",
    layout="wide",
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


def keyword_hits(text: str, keywords: set) -> int:
    t = normalize_text(text)
    return sum(1 for kw in keywords if kw in t)



def analyze_attribution(self_text: str, friend_text: str) -> Tuple[str, str]:
    self_external = keyword_hits(self_text, EXTERNAL_KEYWORDS)
    self_internal = keyword_hits(self_text, INTERNAL_KEYWORDS)
    friend_external = keyword_hits(friend_text, EXTERNAL_KEYWORDS)
    friend_internal = keyword_hits(friend_text, INTERNAL_KEYWORDS)

    if (self_external >= self_internal + 1) and (friend_internal >= friend_external + 1):
        return (
            "Strong self-serving bias signal",
            "You seem more likely to explain your own loss with outside factors, while explaining your friend's loss with personal mistakes.",
        )
    if (self_external > self_internal) and (friend_internal > friend_external):
        return (
            "Moderate self-serving bias signal",
            "Your wording suggests a softer version of the same pattern: external reasons for yourself, internal reasons for your friend.",
        )
    if (self_internal > self_external) and (friend_internal > friend_external):
        return (
            "More self-critical pattern",
            "You appear willing to assign personal responsibility to both yourself and your friend, which can reduce self-serving bias.",
        )
    if (self_external > self_internal) and (friend_external > friend_internal):
        return (
            "External attribution pattern",
            "You seem to explain losses mainly through outside conditions for both people. This may reduce blame, but it can also hide decision errors.",
        )
    return (
        "Mixed attribution pattern",
        "Your answers do not show a clear self-serving pattern. That may mean your reasoning is more balanced, or simply more nuanced than a keyword check can capture.",
    )



def q1_feedback(value: int) -> Tuple[str, str]:
    if value >= 60:
        return (
            "Strong overconfidence signal",
            "A very high forecast may suggest that you are placing a lot of trust in your own forecasting ability. In real investing, one-year growth predictions are usually much harder than they feel.",
        )
    if value >= 40:
        return (
            "Moderate overconfidence signal",
            "Your estimate is still fairly confident. This may reflect a belief that your analysis can identify future outcomes better than average.",
        )
    return (
        "Relatively cautious forecast",
        "Your answer suggests more humility about uncertain growth predictions. That does not guarantee correctness, but it reduces the risk of overconfidence.",
    )



def q2_feedback(choice: str) -> Tuple[str, str]:
    if choice == "Successful":
        return (
            "Representativeness bias signal",
            "You may be inferring that a strong CEO background automatically means a strong company outcome. That shortcut feels convincing, but it is not enough on its own.",
        )
    if choice == "I cannot decide with this information":
        return (
            "Data-conscious response",
            "This answer resists the temptation to build a company forecast from a single narrative cue.",
        )
    return (
        "Possible narrative influence",
        "Your answer may still reflect the CEO story, though less strongly than a direct 'Successful' response.",
    )



def q3_feedback(value: int) -> Tuple[str, str]:
    if 12 <= value <= 20:
        return (
            "Anchoring signal",
            "Your estimate is close to last year's 15% growth. This may mean the initial figure became a mental anchor.",
        )
    if 8 <= value <= 25:
        return (
            "Mild anchoring signal",
            "Your answer is somewhat close to the reference point. The previous year's number may still have influenced you.",
        )
    return (
        "Lower anchoring signal",
        "Your estimate moved more clearly away from the initial 15% reference point.",
    )



def q4_feedback(value: int) -> Tuple[str, str]:
    if value >= 40:
        return (
            "Availability bias signal",
            "A high failure probability may mean recent fintech failure stories became unusually vivid in memory and influenced your judgment.",
        )
    if value >= 20:
        return (
            "Possible availability effect",
            "Your answer may still reflect recent negative news, though less strongly.",
        )
    return (
        "Lower availability signal",
        "Your answer suggests that recent headlines did not dominate your estimate as much.",
    )



def q5_feedback(choice: str) -> Tuple[str, str]:
    score = LIKERT_SCORE[choice]
    if score >= 4:
        return (
            "Illusion of control signal",
            "Agreeing with this statement may mean you are treating access to information as if it creates control over outcomes. Information helps, but it does not remove uncertainty.",
        )
    if score == 3:
        return (
            "Balanced but undecided",
            "You may sense that information matters, while also recognizing that many risks remain outside investor control.",
        )
    return (
        "Lower illusion of control signal",
        "Your answer recognizes that information access is not the same as controlling risk.",
    )



def q6_feedback(choice: str) -> Tuple[str, str]:
    if choice == "CFO":
        return (
            "Cognitive conflict signal",
            "You may be favoring the more human and optimistic message over the tougher but more cautionary audit signal.",
        )
    if choice == "Audit report":
        return (
            "More analytical response",
            "You are giving more weight to the formal risk signal, even though it may feel less emotionally attractive.",
        )
    return (
        "Unresolved conflict",
        "This answer shows that contradictory information created genuine tension, which is a normal part of real financial decisions.",
    )



def q8_feedback(choice: str) -> Tuple[str, str]:
    if choice == "Yes, it was obvious":
        return (
            "Hindsight bias signal",
            "After a failure happens, it is easy to feel that the outcome had been obvious all along. That feeling can distort how we judge the past.",
        )
    if choice == "Not sure":
        return (
            "Partial hindsight resistance",
            "You are not fully rewriting the past, but the event may still feel easier to explain after the fact.",
        )
    return (
        "Lower hindsight bias signal",
        "Your answer recognizes that difficult outcomes are often much less obvious before they happen.",
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
# UI
# -----------------------------

st.title("FinTechX Behavioral Finance Biases App")
st.caption("An interactive classroom survey in English based on common behavioral finance biases.")

st.markdown(
    """
This app presents a short FinTechX case and helps students reflect on **behavioral biases in financial decision-making**.
Answer all questions first, then review the interpretation section.
"""
)

with st.expander("How to use this app", expanded=False):
    st.markdown(
        """
- Complete all questions in the survey.
- Click **Submit Answers**.
- Review your bias signals and the classroom discussion prompts.
- Use the results as a learning tool, not as a formal psychological diagnosis.
"""
    )

with st.form("fintechx_bias_form"):
    st.subheader("Survey Questions")

    q1 = st.slider(
        "1) What do you estimate is the probability that FinTechX will grow by more than 20% in the next 1 year?",
        min_value=0,
        max_value=100,
        value=50,
        help="Select a probability between 0% and 100%.",
    )

    q2 = st.radio(
        "2) FinTechX's CEO is an experienced executive with a Trendyol background. Based on this, what is your first impression of the company's future performance?",
        ["Successful", "Moderate", "Unsuccessful", "I cannot decide with this information"],
    )

    q3 = st.slider(
        "3) FinTechX grew by 15% last year. What is your growth estimate for this year?",
        min_value=0,
        max_value=100,
        value=15,
        help="Enter your forecast as a percentage.",
    )

    q4 = st.slider(
        "4) During this period, fintech failures are frequently discussed in the media. What do you think is the probability that FinTechX will fail?",
        min_value=0,
        max_value=100,
        value=25,
        help="Select a probability between 0% and 100%.",
    )

    q5 = st.radio(
        '5) "If I can regularly access FinTechX\'s financial statements, I believe I can control my risk."',
        ["Strongly agree", "Agree", "Undecided", "Disagree", "Strongly disagree"],
    )

    q6 = st.radio(
        '6) CFO: "The company is doing well." Audit report: "Cash flow is risky." Which source do you trust more?',
        ["CFO", "Audit report", "Undecided"],
    )

    q7a = st.text_area(
        "7a) If you personally lost money, why do you think it happened?",
        placeholder="Write a short explanation...",
        height=120,
    )

    q7b = st.text_area(
        "7b) If your friend lost money, why do you think it happened?",
        placeholder="Write a short explanation...",
        height=120,
    )

    q8 = st.radio(
        "8) FinTechX failed. Was this outcome easy to predict?",
        ["Yes, it was obvious", "No, it was not obvious", "Not sure"],
    )

    submitted = st.form_submit_button("Submit Answers")


if submitted:
    if not q7a.strip() or not q7b.strip():
        st.error("Please answer both Question 7a and Question 7b before continuing.")
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
        st.session_state["responses"] = responses


if "responses" in st.session_state:
    r = st.session_state["responses"]

    st.divider()
    st.header("Your Results")

    c1, c2 = st.columns(2)

    with c1:
        status, explanation = q1_feedback(r["Q1"])
        st.info(f"**Question 1:** {status}\n\n{explanation}")

        status, explanation = q3_feedback(r["Q3"])
        st.info(f"**Question 3:** {status}\n\n{explanation}")

        status, explanation = q5_feedback(r["Q5"])
        st.info(f"**Question 5:** {status}\n\n{explanation}")

        status, explanation = q8_feedback(r["Q8"])
        st.info(f"**Question 8:** {status}\n\n{explanation}")

    with c2:
        status, explanation = q2_feedback(r["Q2"])
        st.info(f"**Question 2:** {status}\n\n{explanation}")

        status, explanation = q4_feedback(r["Q4"])
        st.info(f"**Question 4:** {status}\n\n{explanation}")

        status, explanation = q6_feedback(r["Q6"])
        st.info(f"**Question 6:** {status}\n\n{explanation}")

        status, explanation = analyze_attribution(r["Q7a"], r["Q7b"])
        st.info(f"**Question 7:** {status}\n\n{explanation}")

    st.subheader("Response Summary")
    st.markdown(
        f"""
- **Q1:** {r['Q1']}%
- **Q2:** {r['Q2']}
- **Q3:** {r['Q3']}%
- **Q4:** {r['Q4']}%
- **Q5:** {r['Q5']}
- **Q6:** {r['Q6']}
- **Q7a:** {r['Q7a']}
- **Q7b:** {r['Q7b']}
- **Q8:** {r['Q8']}
"""
    )

    st.divider()
    st.header("Bias Explanations for Class Discussion")

    for title, details in BIAS_DETAILS.items():
        with st.expander(title, expanded=False):
            st.markdown(f"**Observation**\n\n{details['observation']}")
            st.markdown(f"**Why this is a bias**\n\n{details['why']}")
            st.markdown("**Possible impact on financial decisions**")
            for item in details["impact"]:
                st.markdown(f"- {item}")
            st.markdown("**Discussion questions**")
            for item in details["discussion"]:
                st.markdown(f"- {item}")

    st.divider()
    st.subheader("Instructor Note")
    st.write(
        "This tool is designed for educational reflection. A student's answer does not prove that a bias is present; it only helps make the bias visible for discussion."
    )

    summary_lines = [
        "Question,Response",
        f'Q1,"{r["Q1"]}%"',
        f'Q2,"{r["Q2"]}"',
        f'Q3,"{r["Q3"]}%"',
        f'Q4,"{r["Q4"]}%"',
        f'Q5,"{r["Q5"]}"',
        f'Q6,"{r["Q6"]}"',
        f'Q7a,"{r["Q7a"].replace(chr(34), chr(39))}"',
        f'Q7b,"{r["Q7b"].replace(chr(34), chr(39))}"',
        f'Q8,"{r["Q8"]}"',
    ]
    csv_text = "\n".join(summary_lines)
    st.download_button(
        "Download responses as CSV",
        data=csv_text,
        file_name="fintechx_bias_responses.csv",
        mime="text/csv",
    )
else:
    st.warning("Submit the survey to see interpretations and class discussion content.")
