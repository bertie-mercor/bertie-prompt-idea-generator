import streamlit as st
import json
import re
from openai import OpenAI

# Init OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Prompt Generator")

# Initialize session state
if "ideas_investment" not in st.session_state:
    st.session_state.ideas_investment = []
if "ideas_medicine" not in st.session_state:
    st.session_state.ideas_medicine = []

# Tool schema for structured response
tools = [{
    "type": "function",
    "function": {
        "name": "return_list",
        "description": "Return a list of items.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["items"]
        }
    }
}]

def generate_ideas(domain_instruction, previous_ideas):
    prompt = domain_instruction
    if previous_ideas:
        prompt = f"Here are previous prompt ideas:\n\n{json.dumps(previous_ideas, indent=2)}\n\n" + prompt
        prompt += f"\nMake sure these new 5 prompts are diverse from the above."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "return_list"}}
    )

    arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    return arguments["items"]

# Instructions for each domain
instruction_investment = """
I want you to create 5 example prompts that an investment analyst at a bank would input to a frontier AI model to help them in their day-to-day work. Return a list of real prompts.

Guidelines:
- Use real companies, metrics, measures, and values. No placeholders.
- Only focus on companies with SEC filings. No macroeconomic analysis.
- Avoid examples that require regression or sophisticated tooling.
"""

instruction_medicine = """
I want you to create 5 example prompts that a medical researcher or doctor would input to a frontier AI model to help them in their day-to-day work. Return a list of real prompts.

Guidelines:
- Use real clinical problems, diseases, tests, drug names, and medical processes.
- No placeholder names or invented medications.
- Ensure prompts are applicable to day-to-day healthcare practice or research.
"""

# Investment Banking Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("💼 Investment Banking: Generate 5"):
        st.session_state.ideas_investment = generate_ideas(instruction_investment, [])
        st.success("Generated 5 new investment ideas.")

with col2:
    if st.button("🩺 Medicine: Generate 5"):
        st.session_state.ideas_medicine = generate_ideas(instruction_medicine, [])
        st.success("Generated 5 new medical ideas.")


# Medicine Buttons
col3, col4 = st.columns(2)
with col3:
    if st.button("➕ Investment Banking: Generate 5 More"):
        more = generate_ideas(instruction_investment, st.session_state.ideas_investment)
        st.session_state.ideas_investment.extend(more)
        st.success("Added 5 more investment ideas.")

with col4:
    if st.button("➕ Medicine: Generate 5 More"):
        more = generate_ideas(instruction_medicine, st.session_state.ideas_medicine)
        st.session_state.ideas_medicine.extend(more)
        st.success("Added 5 more medical ideas.")


# Display ideas
if st.session_state.ideas_investment:
    st.subheader("📋 Investment Banking Prompts")
    for i, idea in enumerate(st.session_state.ideas_investment, 1):
        cleaned = re.sub(r'^\s*\d+[\.\)]\s*', '', idea).strip(' "\'')
        st.markdown(f"{i}. {cleaned}")

if st.session_state.ideas_medicine:
    st.subheader("📋 Medicine Prompts")
    for i, idea in enumerate(st.session_state.ideas_medicine, 1):
        cleaned = re.sub(r'^\s*\d+[\.\)]\s*', '', idea).strip(' "\'')
        st.markdown(f"{i}. {cleaned}")
