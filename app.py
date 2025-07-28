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
- Comparisons are really powerful, such as comparing over time or across companies. But don't make every question a comparison!
- Slightly abstract queries are great too, such as giving an abstract concept (e.g., strength, liquidity, growth) and letting the answer work out what it means.
- You should not refer directly to the SEC filing unless it's actually necessary.
- You can refer to entire industries, e.g., Airlines, Insurance, Consumer Stapes. 
- You can be forward looking, e.g., assess what will happen given past behavior or if certain assumptions continue (e.g., linear revenue growth). 

Examples of suitable topics and subtopics:

1. Financial Modeling & Analytics
	•	Time Series and Forecasting
	•	Volatility & Risk Modeling
	•	Profit-Loss
	•	Return on Investment Analysis

2. Financial Planning & Investment Advice
	•	Stock Investing / Portfolio Management
	•	Real Estate Investment
	•	Retirement Planning
	•	Debt Management / Credit Score Improvement
	•	Budget / Expense Management

3. Investment Strategy & Portfolio Design
	•	Asset Allocation / Diversification
	•	Hedging & Risk Mitigation
	•	Derivatives (Options, Futures, Swaps)
	•	Insurance
	•	Risk Assessment & Monitoring

4. Financial Technology (FinTech)
	•	Blockchain and Cryptocurrencies
	•	Digital Payment & Lending
	•	Insurtech (Insurance Technology)

5. Corporate Finance
	•	Earnings Report Reasoning
	•	Investment Decision & Capital Budgeting
	•	Capital Structure & Financing Strategy
	•	Mergers & Acquisitions; Valuation, Corporate Restructuring
	•	Corporate Governance

6. Regulation & Ethics
	•	Banking & Financial Regulation Compliance
	•	Anti-Money Laundering
	•	Insurance Regulation
	•	Corporate Governance
	•	Ethic Standards, Consumer Protection & Data Privacy

7. International Finance
	•	International Investment & FOREX
	•	Exchange Rates
	•	International Financial Institutions
	•	Trade Finance
	•	Export-Import Pricing
	•	Foreign Exchange Risk Management

8. Taxation & Filing Guidance
	•	Individual Income & Family Tax Planning
	•	Business & Self-Employment Taxation
	•	International & Cross-Border Tax Issues
	•	Filing Processes, Filing Guidance & Compliance

9. Accounting & Bookkeeping Practices
	•	Transaction Recording & Reconciliation
	•	Financial Statement Preparation & GAAP/IFRS Reporting
	•	Cost & Managerial Accounting
	•	Internal Controls, Audit & Compliance Readiness

10. Financial Markets and Institutions
	•	Money Markets & Capital Markets
	•	Banking & Financial Intermediation
	•	Non-Bank Financial Institutions
	•	Financial Market Regulation & Systemic Risk
"""

instruction_medicine = """
I want you to create 5 example prompts that a medical researcher or doctor would input to a frontier AI model to help them in their day-to-day work. Return a list of real prompts.

Guidelines:
- Use real clinical problems, diseases, tests, drug names, and medical processes.
- No placeholder names or invented medications.
- Ensure prompts are applicable to day-to-day healthcare practice or research.

Examples of suitable topics and subtopics, with example focuses

1. Clinical Decision Support
 • Supporting Diagnostic Decisions: Differential for chest pain, causes of syncope, diagnostic approach to jaundice
 • Planning Treatments: Medications, dosing, side effects, Procedures, timing, risks, Diet, exercise, physical therapy, CBT, therapy vs. meds, Folk remedies, supplements
 • Predicting Risks and Outcomes: Stroke risk post-TIA, 10-year ASCVD risk, likelihood of sepsis complications
 • Emergency Referrals: When to refer for surgical abdomen, red flags in back pain needing ER visit
 • Providing Clinical Knowledge Support: Treatment guidelines for COPD, evidence summary on beta blockers in heart failure
 • Screening & Clinical Preventive Care Decisions: Age to start colonoscopy, breast cancer screening for BRCA carriers, immunization decisions
 
2. Health and Wellness
 • Lifestyle & Behavior Modification Support: “What changes can I make to reduce my heart disease risk?”, “How do I stop emotional eating?”, “How can I stick to my medication plan?”, “What strategies help with taking pills regularly?”
 • Nutrition & Diet Reasoning: “Which diet is better for prediabetes?”, “Is intermittent fasting safe for me?”
 • Fitness & Physical Activity Planning: “What exercises are safe for someone with osteoporosis?”, “Can I lift weights with high blood pressure?”
 • Sleep Hygiene & Optimization: “How can I improve my sleep if I have insomnia?”, “What bedtime routine works for shift workers?”
 • Mental Wellness Monitoring: “How do I know if I’m experiencing burnout or depression?”, “What are early signs of anxiety?”

3. Medical Research Assistance
 • Conducting Literature Research: Finding RCTs on statins in elderly, summarizing Cochrane reviews, Is this research study of good quality
 • Analyzing Clinical Research Data: Interpreting survival curves, comparing outcomes between cohorts
 • Clinical Research Study Design & Methodology: What is the difference between cohort and case-control studies?
 • Clinical Research Ethics & Compliance: What ethical issues arise in placebo-controlled cancer trials?

4. Public Health, Policy & Systems
 • Population Health Interventions: Population-level Vaccination Strategy Reasoning, Clean Water & Sanitation Planning
 • Epidemiology & Surveillance: Outbreak Detection & Response Reasoning, Contact Tracing Logic
 • Health/Medical Ethics & Equity: Informed Consent, Bias in Diagnosis and Treatment
 • Health/Medical Policy & Bylaws: Medical Bylaws & Guidelines
 • Good Medical Practices: Safety, infection control
 • Good Laboratory Practices: Lab handling, protocol
 • Social Determinants of Health: Housing, food access
 • Navigating Healthcare Providers & Facilities: Insurance, access, delivery

"""


# Col 2
col1, col2 = st.columns(2)
with col1:
    if st.button("💼  Investment Banking: 5 More"):
        more = generate_ideas(instruction_investment, st.session_state.ideas_investment)
        st.session_state.ideas_investment.extend(more)
        st.success("Added 5 more investment ideas.")

with col2:
    if st.button("🩺  Medicine: 5 More"):
        more = generate_ideas(instruction_medicine, st.session_state.ideas_medicine)
        st.session_state.ideas_medicine.extend(more)
        st.success("Added 5 more medical ideas.")


# # Col 1
# col1, col2 = st.columns(2)
# with col1:
#     if st.button("💼  Investment Banking: Generate 5 more"):
#         st.session_state.ideas_investment = generate_ideas(instruction_investment, [])
#         st.success("Generated 5 new investment ideas.")

# with col2:
#     if st.button("🩺  Medicine: Generate 5 more"):
#         st.session_state.ideas_medicine = generate_ideas(instruction_medicine, [])
#         st.success("Generated 5 new medical ideas. If you also generated IB ideas, these appear below.")


# # Col 2
# col3, col4 = st.columns(2)
# with col3:
#     if st.button("💼  Investment Banking: 5 More"):
#         more = generate_ideas(instruction_investment, st.session_state.ideas_investment)
#         st.session_state.ideas_investment.extend(more)
#         st.success("Added 5 more investment ideas.")

# with col4:
#     if st.button("🩺  Medicine: 5 More"):
#         more = generate_ideas(instruction_medicine, st.session_state.ideas_medicine)
#         st.session_state.ideas_medicine.extend(more)
#         st.success("Added 5 more medical ideas.")


# Display ideas
if st.session_state.ideas_investment:
    st.subheader("📋 Investment Banking Prompt Ideas")
    for i, idea in enumerate(st.session_state.ideas_investment, 1):
        cleaned = re.sub(r'^\s*\d+[\.\)]\s*', '', idea).strip(' "\'')
        st.markdown(f"{i}. {cleaned}")

if st.session_state.ideas_medicine:
    st.subheader("📋 Medicine Prompt Ideas")
    for i, idea in enumerate(st.session_state.ideas_medicine, 1):
        cleaned = re.sub(r'^\s*\d+[\.\)]\s*', '', idea).strip(' "\'')
        st.markdown(f"{i}. {cleaned}")
