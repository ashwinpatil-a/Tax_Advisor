from tax_rules import tax_rules_engine

def get_tax_saving_suggestions(deductions):
    """Generates personalized tax-saving suggestions with simple, descriptive titles."""
    suggestions = []
    max_potential_deductions = {}

    # Suggestion for General Investments
    limit_80c = tax_rules_engine.get_deduction_limit('section_80c', 'limit')
    current_80c = deductions.get('section_80c', 0)
    if current_80c < limit_80c:
        suggestions.append({
            "title": f"Maximize Investments (PPF, EPF, etc.)",
            "details": f"You can invest ₹{limit_80c - current_80c:,.0f} more in options like PPF, ELSS, or Life Insurance to reach your full ₹{limit_80c:,.0f} limit."
        })
    max_potential_deductions['section_80c'] = limit_80c
    
    # Suggestion for NPS
    limit_nps = tax_rules_engine.get_deduction_limit('section_80ccd_1b', 'limit')
    current_nps = deductions.get('section_80ccd_1b', 0)
    if current_nps < limit_nps:
        suggestions.append({
            "title": f"Invest in Pension Plan (NPS)",
            "details": f"Save up to ₹{limit_nps - current_nps:,.0f} more in taxes by investing in the National Pension System (NPS), which is an extra benefit."
        })
    max_potential_deductions['section_80ccd_1b'] = limit_nps

    return suggestions, max_potential_deductions

def get_financial_wellness_suggestions(income, deductions, potential_tax_savings):
    """Generates financial wellness tips."""
    suggestions = []
    total_income = income['salary']['salary_total'] + income['other_sources']

    if potential_tax_savings > 1000:
        monthly_saving = potential_tax_savings / 12
        suggestions.append({
            "title": "Automate Your Wealth Creation",
            "details": f"Saving ₹{potential_tax_savings:,.0f} in tax gives you an extra ₹{monthly_saving:,.0f} each month. Start a Systematic Investment Plan (SIP) to automatically grow this money."
        })
    elif total_income > 500000:
        suggestions.append({
            "title": "Begin Your Investment Journey",
            "details": "Even small, regular investments can create significant wealth over time. Consider starting a monthly SIP of just ₹5,000 in a diversified mutual fund."
        })

    # Suggestion for Health Insurance
    if deductions.get('section_80d_self', 0) == 0:
        suggestions.append({
            "title": "Secure Your Health & Finances",
            "details": "Medical emergencies can be costly. A health insurance policy is crucial for financial security and also provides tax benefits."
        })
    
    # Suggestion for Term Insurance
    if total_income > 700000:
        suggestions.append({
            "title": "Protect Your Family's Future",
            "details": f"A term life insurance policy can secure your family's future at a very low cost. Premiums are deductible under the general tax-saving investments category."
        })

    return suggestions