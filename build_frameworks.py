import json

frameworks = {
  "Pricing": [
    "### Pricing Framework",
    "- **Data**: Experience vs. Industry, internal vs. external credibility.",
    "- **Assumptions (Demographic)**: Morbidity, Mortality, Selection effects.",
    "- **Assumptions (Financial)**: Interest rates/Yield curves, Expenses (initial/renewal/claim), Medical inflation.",
    "- **Formula**: Equation of value vs. Cashflow modeling, stochastic vs. deterministic.",
    "- **Profitability & Capital**: Target return on capital, margin for risk/uncertainty, capital cost.",
    "- **Commercial Constraints**: Competitor rates (benchmarking), cross-subsidy, saleability.",
    "- **Sensitivity & Options**: Testing sensitivity to lapse rates and option-take up."
  ],
  "Claims Management": [
    "### Claims Management Process",
    "- **Notification & Proof**: Clear definitions, documentation required, verification of pre-existing conditions.",
    "- **Assessment / Triage**: Non-disclosure checks, tele-interviews, use of specialized medical officers.",
    "- **Control & Mitigation**: Home visits (IP), second opinions, independent medical exams.",
    "- **Rehabilitation (IP)**: Early intervention, proportionate benefits for partial return, funding treatment to reduce claim duration.",
    "- **Payment / Settlement**: Annuity vs lump sum, tax implications, currency, avoiding over-insurance."
  ],
  "Regulation": [
    "### Regulatory / Compliance Framework",
    "- **Prudential Regulation**: Solvency capital rules (SCR/MCR under Solvency II / IRDAI), statutory reserving.",
    "- **Business Conduct / Consumer Protection**: Treating Customers Fairly (TCF), clear policy wording, cooling-off periods.",
    "- **Pricing Constraints**: Gender-neutral pricing (EU), community rating vs. age-banded.",
    "- **Data Protection**: GDPR or local data privacy laws limits underwriting questions (e.g. genetic testing restrictions).",
    "- **Systemic / State Interaction**: Means-tested benefits, integration with National Health (PMJAY)."
  ],
  "Underwriting": [
    "### Underwriting Strategy",
    "- **Objective**: Prevent anti-selection, classify risks equitably, maintain competitor parity.",
    "- **Methods**: Medical (files, exams) vs. Non-Medical (questionnaires, tele-interviewing).",
    "- **Alternative Approaches**: Moratorium underwriting (often PMI), Free Cover Limits (Group).",
    "- **Outcomes**: Standard rates, rated premiums (+%), exclusions, deferral, decline.",
    "- **Operational**: Cost vs. Value of info, speed of onboarding (straight-through processing)."
  ],
  "Risk Management & Capital": [
    "### Risk Framework",
    "- **Risk Types**: Market/Investment, Default/Credit, Underwriting (Mortality/Lapse/Expense), Operational.",
    "- **Quantification**: Stress and Scenario testing, Internal Models vs. Standard Formula.",
    "- **Mitigation**: Reinsurance, Asset-Liability Matching (ALM), product redesign (reviewable premiums), stricter claims control.",
    "- **Capital**: Economic capital vs. Regulatory capital, risk appetite statements, diversification benefits."
  ],
  "Reserving & Valuation": [
    "### Reserving Principles",
    "- **Components**: Mathematical reserves (BEL), Risk Margin, Unearned Premium Reserve (UPR), Outstanding Claims (OSLR), IBNR.",
    "- **Methods**: Bornhuetter-Ferguson, Chain Ladder / Run-off triangles (short-tailed), Cashflow projection (long-tailed).",
    "- **Differences**: Pricing (realistic + profit margin) vs. Supervisory (prudent/margins) vs. Embedded Value (market consistent).",
    "- **Prudence**: Allowance for adverse deviation, discounting at risk-free rates."
  ],
  "Reinsurance": [
    "### Reinsurance Benefits",
    "- **Financial**: Capital relief, profit smoothing, increase capacity.",
    "- **Risk**: Transfer large single risks (Surplus), catastrophic events (Cat XL), aggregate shocks (Stop Loss).",
    "- **Strategic**: 'Badging' / white-labeling, new market entry, technical underwriting assistance.",
    "- **Types**: Proportional (Quota Share / Surplus) vs. Non-proportional (Excess of Loss)."
  ],
  "Product Design": [
    "### Product Design Elements",
    "- **Needs**: Target market demand, filling State gaps.",
    "- **Features**: Core benefits, waiting periods/deferred periods, exclusions, riders/add-ons.",
    "- **Constraints**: Systems and Admin capabilities, Reinsurance availability, sales channel ease-of-sale.",
    "- **Risks**: Moral hazard, anti-selection, uninsurable risks.",
    "- **Pricing/Capital**: Ensuring the intended design is actually profitable and capital efficient."
  ],
  "Data & Models": [
    "### Data & Modeling Framework",
    "- **Data Issues**: Lack of volume, heterogeneity, changes in internal processes, coding errors, lags in reporting.",
    "- **Solutions**: Reinsurer data, Population proxies (adjusted), Grouping data.",
    "- **Model Choice**: Multi-state (Markov) vs. Formula/Equation of Value. Deterministic vs Stochastic.",
    "- **Governance**: Peer review, backtesting against actual experience, sensitivity testing."
  ],
  "Group Products": [
    "### Group Protection Features",
    "- **Structure**: Master policyholder (Employer), simplified admin, cheaper unit costs.",
    "- **Underwriting**: Free Cover Limits (FCL), 'actively at work' condition, minimal medical info.",
    "- **Risks**: Concentration risk (one building explodes), anti-selection if voluntary take-up, changing workforce demographics.",
    "- **Pricing**: Experience rating (past claims) vs. Community rating, 1 or 3-year rate guarantees."
  ],
  "Investments": [
    "### Investment & ALM Strategy",
    "- **Nature of Liabilities**: Currency, term/duration, fixed vs real (inflation-linked).",
    "- **Matching**: Match duration to immunize against yield curve shifts. Real assets (Equities/Property) for inflation, fixed-interest for non-linked.",
    "- **Constraints**: Regulatory limitations on asset classes, Liquidity needs (PMI claims are sudden), Solvency II capital charges on risky assets."
  ],
  "Professional Guidance": [
    "### Professional Actuarial Duties",
    "- **Standards**: Following APS/TAS (e.g. TAS 100), ensuring advice is clear, comprehensive, and unbiased.",
    "- **Role**: Statutory duties (Chief Actuary / With-Profits Actuary), Peer review requirements.",
    "- **Ethics**: Whistleblowing, managing conflicts of interest, handling data quality issues responsibly."
  ],
  "Capital & Solvency": [
    "### Capital Assessment",
    "- **Role of Capital**: Provide confidence to policyholders and regulators, buffer against shocks.",
    "- **Solvency II**: Pillar 1 (Quantitative: BEL, Risk Margin, SCR), Pillar 2 (Qualitative: ORSA, Governance), Pillar 3 (Disclosure).",
    "- **Management**: Optimizing capital via Reinsurance or ALM, Return on Capital (ROC) thresholds."
  ],
  "Private Medical Insurance (PMI)": [
    "### PMI Specifics",
    "- **Nature**: Short-term (annual renewable), high frequency/low severity claims.",
    "- **Pricing**: Community rating, Age-banding, Medical inflation is a massive driver (super-inflation).",
    "- **Claims**: Pre-authorization, Provider networks, Excesses/Co-payments to reduce trivial claims.",
    "- **Underwriting**: Moratorium is very common, FMU (Full Medical) for comprehensive cover."
  ],
  "Critical Illness": [
    "### CI Specifics",
    "- **Nature**: Long-term, fixed lump-sum payment upon diagnosis of defined condition.",
    "- **Risks**: Changes in medical science (earlier diagnosis), anti-selection, definition disputes.",
    "- **Features**: Survival period (usually 14-28 days), standalone vs accelerated (attached to life cover), severity-based payouts."
  ],
  "Income Protection": [
    "### IP Specifics",
    "- **Nature**: Replacement of lost earnings due to incapacity. Regular payments.",
    "- **Key Levers**: Deferred period (DP) length, Replacement Ratio (max 50-75% to maintain incentive to work).",
    "- **Definition**: Own occupation vs Any occupation vs Activities of Daily Work.",
    "- **Risks**: Moral hazard, economic downturns heavily increase claim rates ('unemployment disguise')."
  ],
  "Pricing & Rating": [
    "### Rating Strategies",
    "- **Age/Gender**: Classic variables (though gender restricted in EU).",
    "- **Experience Rating**: Adjusting renewal premiums based on past group claims.",
    "- **NCD**: No Claims Discounts (common in PMI) to prevent trivial claims but hurts retention if lost.",
    "- **Reviewability**: Guaranteed (fixed) vs Reviewable (can hike rates if experience worsens over the block)."
  ],
  "State Healthcare & Demographics": [
    "### State vs Private Interaction",
    "- **State Role**: Universal coverage (PMJAY / NHS), means-tested social care.",
    "- **Private Role**: Que-jumping, luxury facilities, covering non-critical procedures.",
    "- **Demographics**: Aging populations increase LTC and medical costs, shrinking taxpayer bases.",
    "- **Healthcare Economics**: QALYs (Quality Adjusted Life Years) to decide drug funding via agencies like NICE."
  ],
  "Long-Term Care (LTC)": [
    "### LTC Specifics",
    "- **Nature**: Payout triggered by failure of Activities of Daily Living (ADLs) or cognitive impairment.",
    "- **Types**: Pre-funded (regular premiums while healthy) vs Immediate Needs Annuity (lump sum at point of care).",
    "- **Risks**: Extreme longevity risk, massive care-cost inflation, reputational risk if claims denied in old age."
  ],
  "Legislation & Taxation": [
    "### Tax & Law Impacts",
    "- **Premiums/Benefits**: Are premiums tax deductible? Are benefits tax free? Drives product demand.",
    "- **Employer Tax**: Incentivizes Group PMI / Group IP if treated favorably as business expense.",
    "- **Anti-Discrimination**: Equality acts preventing pricing based on genetics, gender, or disabilities without pure statistical proof."
  ],
  "Product Design (Protection)": [
    "### General Protection Framework",
    "- **Standalone vs Riders**: Selling CI or Death cover attached to a savings/mortgage plan.",
    "- **Unit-Linked**: Charging mortality/morbidity costs by deducting units from a fund (reviewable by nature).",
    "- **Options**: Conversion options, Guaranteed Insurability Options (GIOs) without medicals."
  ],
  "Administration": [
    "### Admin & IT Systems",
    "- **Setup Constraints**: Can legacy IT handle complex tiered benefits or unit-deductions?",
    "- **Customer Journey**: Quotation portals, premium collection methods (Direct Debit).",
    "- **Outsourcing**: Using Third Party Administrators (TPAs) for claims, call centers. Retaining oversight."
  ]
}

with open(r"g:\Girish\IAI\SP1 and SA1 Health and Care\Practice papers\Claude Widgets\data\Topic_Frameworks.json", "w", encoding="utf-8") as f:
    json.dump(frameworks, f, indent=2)
print("Frameworks JSON successfully generated.")
