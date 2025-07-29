from tax_rules import tax_rules_engine


def calculate_hra_exemption(basic_salary, hra_received, rent_paid, is_metro):
    """Calculates House Rent Allowance (HRA) exemption."""
    if not (basic_salary > 0 and hra_received > 0 and rent_paid > 0):
        return 0

    # HRA exemption is the minimum of:
    # 1. Actual HRA received
    val1 = hra_received
    # 2. Rent paid minus 10% of basic salary
    val2 = rent_paid - (0.10 * basic_salary)
    # 3. 50% of basic salary for metro cities, 40% for non-metro
    rate = tax_rules_engine.get_deduction_limit(
        'hra', 'metro_rate' if is_metro else 'non_metro_rate'
    )
    val3 = rate * basic_salary

    return max(0, min(val1, val2, val3))


def calculate_tax_on_income(taxable_income, regime, profile):
    """Calculates income tax based on slab rates."""
    slabs_by_age = tax_rules_engine.get_slabs(regime)
    age_group = profile['age_group']

    if regime == 'old' and profile['resident_status'] == 'resident':
        slabs = slabs_by_age.get(age_group, slabs_by_age['below_60'])
    else:
        # New regime has same slabs for all ages; same for non-residents under old regime
        slabs = slabs_by_age if regime == 'new' else slabs_by_age['below_60']

    tax = 0
    remaining_income = taxable_income
    sorted_slabs = sorted([s for s in slabs if 'upto' in s], key=lambda x: x['upto'])
    above_slab = next((s for s in slabs if 'above' in s), None)

    last_slab_limit = 0
    for slab in sorted_slabs:
        limit = slab['upto']
        rate = slab['rate']

        if remaining_income > 0:
            taxable_in_slab = min(remaining_income, limit - last_slab_limit)
            tax += taxable_in_slab * rate
            remaining_income -= taxable_in_slab
            last_slab_limit = limit

    if above_slab and remaining_income > 0:
        tax += remaining_income * above_slab['rate']

    return tax


def calculate_final_tax(profile, income, deductions, regime):
    """Calculates the final tax liability based on profile, income, deductions, and tax regime."""
    # 1. Salary Income
    hra_exemption = 0
    standard_deduction = tax_rules_engine.get_deduction_limit('standard_deduction')

    if regime == 'old':
        hra_exemption = calculate_hra_exemption(
            income['salary']['salary_basic'],
            income['salary']['salary_hra'],
            deductions['hra_details']['rent_paid'],
            deductions['hra_details']['is_metro']
        )
        taxable_salary = income['salary']['salary_total'] - hra_exemption - standard_deduction
    else:
        taxable_salary = income['salary']['salary_total'] - standard_deduction

    if income['salary']['salary_total'] <= 0:
        taxable_salary = 0

    # 2. House Property Income
    hp_std_deduction_rate = tax_rules_engine.get_deduction_limit('house_property_standard_deduction_rate')
    net_annual_value = income['house_property']['hp_rent_received'] - income['house_property']['hp_municipal_taxes']
    hp_std_deduction = net_annual_value * hp_std_deduction_rate
    hp_interest_deduction = min(
        deductions.get('section_24b', 0),
        tax_rules_engine.get_deduction_limit('section_24b', 'limit')
    )
    income_from_hp = net_annual_value - hp_std_deduction - hp_interest_deduction

    # 3. Gross Total Income (GTI)
    gti = (
        max(0, taxable_salary) +
        income.get('capital_gains', 0) +
        income.get('business_profession', 0) +
        income.get('other_sources', 0) +
        income_from_hp
    )

    # 4. Taxable Income
    taxable_income = gti
    if regime == 'old':
        chapter_via_deductions = 0

        chapter_via_deductions += min(
            deductions.get('section_80c', 0),
            tax_rules_engine.get_deduction_limit('section_80c', 'limit')
        )
        chapter_via_deductions += min(
            deductions.get('section_80ccd_1b', 0),
            tax_rules_engine.get_deduction_limit('section_80ccd_1b', 'limit')
        )

        limit_80d_self = tax_rules_engine.get_deduction_limit(
            'section_80d',
            'limit_self_above_60' if deductions['self_above_60'] else 'limit_self_below_60'
        )
        chapter_via_deductions += min(deductions.get('section_80d_self', 0), limit_80d_self)

        limit_80d_parents = tax_rules_engine.get_deduction_limit(
            'section_80d',
            'limit_parents_above_60' if deductions['parents_above_60'] else 'limit_parents_below_60'
        )
        chapter_via_deductions += min(deductions.get('section_80d_parents', 0), limit_80d_parents)

        chapter_via_deductions += deductions.get('section_80e', 0)

        # Section 80G (Donations)
        adjusted_gti_for_80g = gti - chapter_via_deductions
        donation_limit = 0.10 * adjusted_gti_for_80g
        eligible_donation = min(deductions.get('section_80g', 0), donation_limit)
        chapter_via_deductions += eligible_donation * 0.50  # Assuming 50% eligible

        # Disabilities - 80U and 80DD
        if deductions.get('section_80u') == 'disability':
            chapter_via_deductions += tax_rules_engine.get_deduction_limit('section_80u', 'disability')
        elif deductions.get('section_80u') == 'severe_disability':
            chapter_via_deductions += tax_rules_engine.get_deduction_limit('section_80u', 'severe_disability')

        if deductions.get('section_80dd') == 'disability':
            chapter_via_deductions += tax_rules_engine.get_deduction_limit('section_80dd', 'disability')
        elif deductions.get('section_80dd') == 'severe_disability':
            chapter_via_deductions += tax_rules_engine.get_deduction_limit('section_80dd', 'severe_disability')

        # 80TTA - Savings account interest
        savings_interest = income.get('other_sources_interest_savings', 0)
        chapter_via_deductions += min(
            savings_interest,
            tax_rules_engine.get_deduction_limit('section_80tta', 'limit')
        )

        taxable_income = max(0, gti - chapter_via_deductions)

    # 5. Calculate Tax and Cess
    income_tax = calculate_tax_on_income(taxable_income, regime, profile)

    # Section 87A rebate
    rebate_limit = 500000 if regime == 'old' else 700000
    if taxable_income <= rebate_limit and profile['resident_status'] == 'resident':
        income_tax = 0

    cess = income_tax * tax_rules_engine.get_cess_rate()
    total_tax = round(income_tax + cess)

    return {
        "taxable_income": taxable_income,
        "total_tax": total_tax,
        "gti": gti,
        "income_tax": income_tax,
        "cess": cess
    }
