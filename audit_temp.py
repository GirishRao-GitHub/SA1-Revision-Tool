import json
import re

# Extract MASTER_TAXONOMY from the HTML content manually since I have it
taxonomy = {
  "Pricing": ["Data & Assumptions", "Risk Profile", "Expenses", "Profit Margin", "Cross-subsidy", "Sensitivity Analysis", "Return on Capital", "Equation of Value", "Cashflow Techniques"],
  "Claims Management": ["Definitions", "Rehabilitation", "Fraud & Verification", "Reserving", "Claim Control", "Return to Work", "Assessment of claims"],
  "Regulation": ["Treating Customers Fairly", "Capital Requirements", "Taxation", "State Provision", "IRDAI", "Compliance", "Policyholder Protection Schemes", "Solvency II Framework"],
  "Underwriting": ["Anti-selection", "Financial Underwriting", "Medical Underwriting", "Free Cover Limits", "Tele-underwriting", "Genetic Testing", "Pre-existing Conditions"],
  "Data": ["Credibility", "Heterogeneity", "Proxies", "AI & Machine Learning", "Data Quality", "Completeness", "Accuracy", "Timeliness"],
  "Models": ["Backtesting", "Sensitivity", "Model Governance", "Stochastic & Deterministic", "Multi-state Models", "Formula", "Equation of Value", "Projection"],
  "Reserving & Valuation": ["IBNR / IBNER", "Bornhuetter-Ferguson", "Run-off Triangles", "Best Estimate Liabilities", "Risk Margin", "Prudence", "Supervisory Reserves", "Market Consistent Valuation"],
  "Risk Management & Capital": ["Economic Capital", "Stress Testing", "Asset Liability Management", "Risk Appetite", "Concentration of Risk", "Pandemics", "Catastrophes", "Options & Guarantees", "Climate Risks"],
  "Reinsurance": ["Risk Transfer", "Capital Relief", "Technical Assistance", "Quota Share", "Excess of Loss", "Catastrophe Cover", "Retention Optimization", "Badging"],
  "Investments": ["Matching", "Liquidity", "Standard Formula", "Internal Models", "Asset Classes", "Yield Curve", "Asset-liability matching strategy"],
  "Product Design": ["Benefits & Conditions", "Target Market", "Options & Guarantees", "Exclusions", "Surrender Values", "Marketability", "Bundling & Unbundling"],
  "Group Products": ["Master Trust", "Take-up Rates", "Administration", "Unit Cost Savings", "Employer Involvement", "Free Cover Limits"],
  "Professional Guidance": ["Actuarial Standards", "Peer Review", "Conflicts of Interest", "Whistleblowing", "Communication", "Data Quality", "Statutory Actuarial Roles"],
  "Capital & Solvency": ["Solvency Capital Requirements (SCR)", "Value at Risk (VaR)", "Return on Capital", "Internal Models", "Solvency II mapping"],
  "Private Medical Insurance (PMI)": ["Moratorium Underwriting", "Community Rating", "Indemnity", "Excesses & Co-payments", "Provider Networks", "Medical Inflation"],
  "Critical Illness": ["Survival Period", "Standard Definitions", "Advances in Medicine", "Accelerated Benefits", "Standalone Cover"],
  "Income Protection": ["Deferred Period", "Replacement Ratio", "Definition of Incapacity", "State Benefits integration", "Rehabilitation"],
  "Pricing & Rating": ["Age Banding", "Community Rating", "Experience Rating", "No Claims Discount (NCD)", "Renewable Premiums"],
  "State Healthcare & Demographics": ["Pradhan Mantri Jan Arogya Yojana (PMJAY)", "Mass Health Schemes", "Aging Population", "QALYs", "Medical Inflation", "Public vs Private funding"],
  "Long-Term Care (LTC)": ["Activities of Daily Living (ADLs)", "Pre-funding vs Immediate Needs", "Cognitive Impairment", "Care Home Costs", "State limitations"],
  "Legislation & Taxation": ["Premium Taxes", "Benefit Taxes", "Profit Taxation", "Employment Law", "Data Protection (GDPR/DPA)"],
  "Product Design (Protection)": ["Guaranteed vs Reviewable premiums", "Term Assurance riders", "Unit-Linked Wrappers", "Renewability"],
  "Administration": ["Policy setup", "Premium Collection", "Lapsation processes", "Customer Service", "Outsourcing / Counterparties"]
}

try:
    with open('data/Topic_Frameworks.json', 'r') as f:
        fw_data = json.load(f)

    gaps = {}
    for theme, subtopics in taxonomy.items():
        if theme not in fw_data:
            gaps[theme] = "MISSING THEME"
            continue
        
        existing_content = " ".join(fw_data[theme]).lower()
        missing_sub = []
        for st in subtopics:
            words = re.findall(r'\w+', st.lower())
            found = any(word in existing_content for word in words if len(word) > 4)
            if not found:
                missing_sub.append(st)
        
        if missing_sub:
            gaps[theme] = missing_sub

    print(json.dumps(gaps, indent=2))
except Exception as e:
    print(f"Error: {e}")
