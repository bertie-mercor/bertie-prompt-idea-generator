import streamlit as st
import json
import re
from openai import OpenAI

# Init OpenAI
#client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
client = OpenAI(api_key = "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")


st.title("Prompt Generator for Investment Analysts")


# Initialize session state
if "ideas" not in st.session_state:
    st.session_state.ideas = []

# Prompt instructions
num_examples = 5
base_instruction = f"""
I want you to create {num_examples} example prompts that an investment analyst at a bank would input to a frontier AI model to help them in their day-to-day work. Return a list of real prompts.

Guidelines:
- Use real companies, metrics, measures, and values. No placeholders.
- Only focus on companies with SEC filings. No macroeconomic analysis.
- Avoid examples that require regression or sophisticated tooling.
"""

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
                    "items": { "type": "string" }
                }
            },
            "required": ["items"]
        }
    }
}]

def generate_ideas(previous_ideas):
    prompt = base_instruction
    if previous_ideas:
        prompt = f"Here are previous prompt ideas:\n\n{json.dumps(previous_ideas, indent=2)}\n\n" + prompt
        prompt += f"\nMake sure these new {num_examples} prompts are diverse from the above."
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "return_list"}}
    )

    arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    return arguments["items"]

# Button: Generate Ideas
if st.button("🟢 Generate Ideas"):
    st.session_state.ideas = generate_ideas([])
    st.success("Generated 5 new ideas.")

# Button: Generate More Ideas
if st.button("🔁 Generate More Ideas"):
    more_ideas = generate_ideas(st.session_state.ideas)
    st.session_state.ideas.extend(more_ideas)
    st.success("Added 5 more ideas.")

# Display ideas
if st.session_state.ideas:
    st.subheader("📋 Generated Ideas")
    for i, idea in enumerate(st.session_state.ideas, 1):
        # Remove leading numbers (e.g. "1." or "2)") and surrounding quotes
        cleaned = re.sub(r'^\s*\d+[\.\)]\s*', '', idea)         # strip leading numbers
        cleaned = cleaned.strip(' "\'')                         # strip leading/trailing quotes and spaces
        st.markdown(f"{i}. {cleaned}")
        


