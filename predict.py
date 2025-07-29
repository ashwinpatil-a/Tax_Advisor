from tax_calculator import calculate_final_tax
from tax_suggester import get_tax_saving_suggestions, get_financial_wellness_suggestions

def run_prediction(profile, income, deductions):
    """
    Runs the tax analysis and generates a simple, direct "Current Best vs. Ultimate Best" response,
    including a detailed breakdown of how the savings are achieved.
    """
    # Step 1: Calculate all possible tax outcomes
    current_tax_old = calculate_final_tax(profile, income, deductions, 'old')
    current_tax_new = calculate_final_tax(profile, income, deductions, 'new')
    
    tax_saving_suggestions, max_deductions_map = get_tax_saving_suggestions(deductions)
    advised_deductions = deductions.copy()
    advised_deductions.update(max_deductions_map)
    advised_tax_old = calculate_final_tax(profile, income, advised_deductions, 'old')
    
    # Step 2: Determine the "Current Best" and "Ultimate Best" options internally
    current_best_data = current_tax_old if current_tax_old['total_tax'] < current_tax_new['total_tax'] else current_tax_new
    ultimate_best_data = advised_tax_old if advised_tax_old['total_tax'] < current_tax_new['total_tax'] else current_tax_new

    # Step 3: Create the detailed savings breakdown with simple, descriptive names
    savings_breakdown = []
    comparison_keys = ['section_80c', 'section_80ccd_1b']
    key_to_name_map = {
        'section_80c': 'Investments (PPF, EPF, etc.)',
        'section_80ccd_1b': 'Pension Plan (NPS)'
    }

    for key in comparison_keys:
        user_amount = deductions.get(key, 0)
        advised_amount = advised_deductions.get(key, 0)
        if advised_amount > user_amount:
            savings_breakdown.append({
                "name": key_to_name_map.get(key, key),
                "user_amount": user_amount,
                "advised_amount": advised_amount
            })

    # Step 4: Prepare the final, simple response
    potential_savings = current_best_data['total_tax'] - ultimate_best_data['total_tax']
    wellness_suggestions = get_financial_wellness_suggestions(income, deductions, potential_savings)
    
    if potential_savings > 0:
        summary = f"Based on your inputs, you can save an additional **₹{potential_savings:,.0f}** per year by following our AI-powered advice!"
    else:
        summary = "You are already doing a great job of optimizing your taxes. There are no further savings based on the information provided."

    return {
        "currentTax": current_best_data,
        "potentialTax": ultimate_best_data,
        "potentialSavings": potential_savings,
        "savingsBreakdown": savings_breakdown,
        "advice": {
            "taxSavingAdvice": tax_saving_suggestions,
            "wellnessAdvice": wellness_suggestions,
        },
        "summary": summary
    }