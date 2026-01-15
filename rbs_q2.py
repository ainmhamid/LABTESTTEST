# app.py
import json
import operator
from typing import Dict, Any, List, Tuple
import streamlit as st

# -----------------------------------
# 1. Rule Engine (Same structure as example)
# -----------------------------------

OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

# -----------------------------------
# 2. Default AC Rules (Based on Table 1)
# -----------------------------------

DEFAULT_RULES = [
    {
        "name": "Windows open → turn AC off",
        "priority": 100,
        "conditions": [
            ["windows_open", "==", True]
        ],
        "action": {
            "mode": "OFF",
            "fan_speed": "LOW",
            "setpoint": "-",
            "reason": "Windows are open"
        }
    },
    {
        "name": "Too cold → turn off",
        "priority": 85,
        "conditions": [
            ["temperature", "<=", 22]
        ],
        "action": {
            "mode": "OFF",
            "fan_speed": "LOW",
            "setpoint": "-",
            "reason": "Already cold"
        }
    },
    {
        "name": "No one home → eco mode",
        "priority": 90,
        "conditions": [
            ["occupancy", "==", "EMPTY"],
            ["temperature", ">=", 24]
        ],
        "action": {
            "mode": "ECO",
            "fan_speed": "LOW",
            "setpoint": "27°C",
            "reason": "Home empty; save energy"
        }
    },
    {
        "name": "Night (occupied) → sleep mode",
        "priority": 75,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["time_of_day", "==", "NIGHT"],
            ["temperature", ">=", 26]
        ],
        "action": {
            "mode": "SLEEP",
            "fan_speed": "LOW",
            "setpoint": "26°C",
            "reason": "Night comfort"
        }
    },
    {
        "name": "Hot & humid (occupied) → cool strong",
        "priority": 80,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 30],
            ["humidity", ">=", 70]
        ],
        "action": {
            "mode": "COOL",
            "fan_speed": "HIGH",
            "setpoint": "23°C",
            "reason": "Hot and humid"
        }
    },
    {
        "name": "Hot (occupied) → cool",
        "priority": 70,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 28]
        ],
        "action": {
            "mode": "COOL",
            "fan_speed": "MEDIUM",
            "setpoint": "24°C",
            "reason": "Temperature high"
        }
    },
    {
        "name": "Slightly warm (occupied) → gentle cool",
        "priority": 60,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 26],
            ["temperature", "<", 28]
        ],
        "action": {
            "mode": "COOL",
            "fan_speed": "LOW",
            "setpoint": "25°C",
            "reason": "Slightly warm"
        }
    }
]

# -----------------------------------
# 3. Rule Evaluation Functions
# -----------------------------------

def evaluate_condition(facts: Dict[str, Any], condition: List[Any]) -> bool:
    field, op, value = condition
    return OPS[op](facts[field], value)

def rule_matches(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    return all(evaluate_condition(facts, cond) for cond in rule["conditions"])

def run_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    fired_rules = [r for r in rules if rule_matches(facts, r)]
    if not fired_rules:
        return {}, []

    fired_rules.sort(key=lambda r: r["priority"], reverse=True)
    return fired_rules[0]["action"], fired_rules

# -----------------------------------
# 4. Streamlit User Interface
# -----------------------------------

st.set_page_config(page_title="Smart AC Controller", layout="wide")
st.title("Rule-Based Smart Home Air Conditioner Controller")

st.sidebar.header("Home Conditions")

temperature = st.sidebar.number_input("Temperature (°C)", value=22)
humidity = st.sidebar.number_input("Humidity (%)", value=46)
occupancy = st.sidebar.selectbox("Occupancy", ["OCCUPIED", "EMPTY"])
time_of_day = st.sidebar.selectbox("Time of Day", ["MORNING", "AFTERNOON", "EVENING", "NIGHT"])
windows_open = st.sidebar.checkbox("Windows Open", value=False)

run = st.sidebar.button("Evaluate")

facts = {
    "temperature": temperature,
    "humidity": humidity,
    "occupancy": occupancy,
    "time_of_day": time_of_day,
    "windows_open": windows_open
}

st.subheader("Current Home Facts")
st.json(facts)

if run:
    action, matched_rules = run_rules(facts, DEFAULT_RULES)

    st.subheader("AC Decision")
    if action:
        st.success(f"""
        **Mode:** {action['mode']}  
        **Fan Speed:** {action['fan_speed']}  
        **Setpoint:** {action['setpoint']}  
        **Reason:** {action['reason']}
        """)
    else:
        st.warning("No matching rule found.")

    st.subheader("Matched Rules (by priority)")
    for rule in matched_rules:
        st.write(f"- **{rule['name']}** (Priority: {rule['priority']})")
