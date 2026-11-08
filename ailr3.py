#Scholarship Advisory Rule-Based System
import streamlit as st
import json
from typing import List, Dict, Any, Tuple
import operator

st.set_page_config(page_title="Scholarship Advisory Rule-Based System", layout="wide")

DEFAULT_RULES: List[Dict[str, Any]] = [
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0]
        ],
        "action": {
            "decision": "AWARD_FULL",
            "reason": "Excellent academic & co-curricular performance, with acceptable need"
        }
    },
    {
        "name": "Good candidate - partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1]
        ],
        "action": {
            "decision": "AWARD_PARTIAL",
            "reason": "Good academic & involvement record with moderate need"
        }
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000]
        ],
        "action": {
            "decision": "REVIEW",
            "reason": "High need but borderline academic score"
        }
    },
    {
        "name": "Low CGPA not eligible",
        "priority": 95,
        "conditions": [
            ["cgpa", "<", 2.5]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "CGPA below minimum scholarship requirement"
        }
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [
            ["disciplinary_actions", ">=", 2]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "Too many disciplinary records"
        }
    }
]

OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

def evaluate_condition(facts: Dict[str, Any], cond: List[Any]) -> bool:
    if len(cond) != 3:
        return False
    field, op, value = cond
    if field not in facts or op not in OPS:
        return False
    try:
        return OPS[op](facts[field], value)
    except Exception:
        return False

def rule_matches(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    return all(evaluate_condition(facts, c) for c in rule.get("conditions", []))

def run_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    fired = [r for r in rules if rule_matches(facts, r)]
    if not fired:
        return ({"decision": "REVIEW", "reason": "No matching rule found; requires manual review."}, [])
    fired_sorted = sorted(fired, key=lambda r: r.get("priority", 0), reverse=True)
    best = fired_sorted[0].get("action", {"decision": "REVIEW", "reason": "No action specified"})
    return best, fired_sorted

# ----------------------------
# Antara Muka Streamlit (UI)
# ----------------------------
st.title("🎓 Scholarship Advisory Rule-Based System")
st.caption("BSD3513 Artificial Intelligence — Lab 3: Knowledge Representation System")

with st.sidebar:
    st.header("Applicant Facts Input")
    cgpa = st.number_input("Cumulative GPA (CGPA)", min_value=0.0, max_value=4.0, step=0.01, value=3.75)
    family_income = st.number_input("Monthly Family Income (RM)", min_value=0.0, max_value=50000.0, step=100.0, value=5000.0)
    co_curricular_score = st.number_input("Co-curricular Score (0-100)", min_value=0, max_value=100, step=1, value=85)
    community_service_hours = st.number_input("Community Service Hours", min_value=0, max_value=500, step=1, value=20)
    semester_study = st.number_input("Current Semester of Study", min_value=1, max_value=10, step=1, value=3)
    disciplinary_actions = st.number_input("Number of Disciplinary Actions", min_value=0, max_value=10, step=1, value=0)

    st.divider()
    st.header("Rule Base Editor (JSON)")
    default_json = json.dumps(DEFAULT_RULES, indent=2)
    rules_text = st.text_area("Edit Rules JSON", value=default_json, height=300)
    evaluate_btn = st.button("Evaluate Application", type="primary")

facts = {
    "cgpa": float(cgpa),
    "family_income": float(family_income),
    "co_curricular_score": int(co_curricular_score),
    "community_service_hours": int(community_service_hours),
    "semester_study": int(semester_study),
    "disciplinary_actions": int(disciplinary_actions),
}

st.subheader("Current Applicant Fact Set")
st.json(facts)

try:
    rules = json.loads(rules_text)
    assert isinstance(rules, list), "Rules must be a JSON array"
except Exception as e:
    st.error(f"Invalid JSON format in rules editor. Falling back to default rules. Details: {e}")
    rules = DEFAULT_RULES

st.divider()

if evaluate_btn:
    action, fired = run_rules(facts, rules)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Evaluation Decision")
        decision = action.get("decision", "REVIEW")
        reason = action.get("reason", "-")
        
        if decision == "AWARD_FULL":
            st.success(f"**Decision: {decision}**\n\n*Reason:* {reason}")
        elif decision == "AWARD_PARTIAL":
            st.info(f"**Decision: {decision}**\n\n*Reason:* {reason}")
        elif decision == "REVIEW":
            st.warning(f"**Decision: {decision}**\n\n*Reason:* {reason}")
        elif decision == "REJECT":
            st.error(f"**Decision: {decision}**\n\n*Reason:* {reason}")
        else:
            st.warning(f"**Decision: {decision}**\n\n*Reason:* {reason}")

    with col2:
        st.subheader("Matched Rules (Ordered by Priority)")
        if not fired:
            st.info("No rules matched the current facts.")
        else:
            for idx, r in enumerate(fired, start=1):
                st.write(f"**{idx}. {r.get('name')}** (Priority: {r.get('priority')})")
                st.caption(f"Action: {r.get('action')}")
                with st.expander(f"View Conditions for Rule {idx}"):
                    for cond in r.get("conditions", []):
                        st.code(str(cond))
else:
    st.info("Configure the applicant facts on the sidebar and click **Evaluate Application**.")