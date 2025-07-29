document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENT SELECTORS ---
    const welcomeScreen = document.getElementById('welcome-screen');
    const taxWizard = document.getElementById('tax-wizard');
    const userEmailLogin = document.getElementById('user-email-login');
    const userEmailFinal = document.getElementById('user-email-final');
    const continueBtn = document.getElementById('continue-btn');
    const taxForm = document.getElementById('tax-form');
    const nextBtns = document.querySelectorAll('.next-btn');
    const prevBtns = document.querySelectorAll('.prev-btn');
    const wizardSteps = document.querySelectorAll('.wizard-step');
    const progressBarSteps = document.querySelectorAll('.progress-bar-step');
    const resultsContainer = document.getElementById('results-container');

    let currentStep = 1;
    const API_BASE_URL = 'http://127.0.0.1:8000'; // Your backend URL

    // --- WIZARD NAVIGATION ---
    const updateProgressBar = () => { progressBarSteps.forEach((step, i) => { if (i + 1 < currentStep) { step.classList.add('completed'); step.classList.remove('active'); } else if (i + 1 === currentStep) { step.classList.add('active'); step.classList.remove('completed'); } else { step.classList.remove('active', 'completed'); } }); };
    const showStep = (stepNumber) => { wizardSteps.forEach(s => s.classList.remove('active')); document.getElementById(`step-${stepNumber}`)?.classList.add('active'); updateProgressBar(); };
    nextBtns.forEach(btn => btn.addEventListener('click', () => { if (currentStep < 4) { currentStep++; showStep(currentStep); } }));
    prevBtns.forEach(btn => btn.addEventListener('click', () => { if (currentStep > 1) { currentStep--; showStep(currentStep); } }));

    // --- API & DATA HANDLING ---
    const getFormData = () => {
        const pFloat = (id) => parseFloat(document.getElementById(id).value) || 0;
        const pBool = (id) => document.getElementById(id).checked;
        const pSelect = (id) => document.getElementById(id).value;
        const pRadio = (name) => document.querySelector(`input[name="${name}"]:checked`)?.value;

        return {
            email: userEmailFinal.value.trim(),
            profile_data: {
                profile: { age_group: pSelect('age-group'), resident_status: pSelect('resident-status') },
                income: {
                    salary: { salary_total: pFloat('salary-total'), salary_basic: pFloat('salary-basic'), salary_hra: pFloat('salary-hra') },
                    house_property: { hp_rent_received: pFloat('hp-rent-received'), hp_municipal_taxes: pFloat('hp-municipal-taxes') },
                    capital_gains: pFloat('capital-gains'), business_profession: pFloat('business-profession'),
                    other_sources: pFloat('other-sources'), other_sources_interest_savings: pFloat('other-sources-interest-savings')
                },
                deductions: {
                    hra_details: { rent_paid: pFloat('rent-paid'), is_metro: (pRadio('is_metro') === 'true') },
                    section_80c: pFloat('section-80c'), section_80ccd_1b: pFloat('section-80ccd-1b'),
                    section_80d_self: pFloat('section-80d-self'), self_above_60: pBool('self-above-60'),
                    section_80d_parents: pFloat('section-80d-parents'), parents_above_60: pBool('parents-above-60'),
                    section_24b: pFloat('section-24b'), section_80e: pFloat('section-80e'),
                    section_80g: 0, section_80u: pSelect('section-80u'), section_80dd: pSelect('section-80dd')
                }
            }
        };
    };
    
    const populateForm = (data) => {
        const sFloat = (id, value) => { if(document.getElementById(id)) document.getElementById(id).value = value || 0; };
        const sBool = (id, value) => { if(document.getElementById(id)) document.getElementById(id).checked = value || false; };
        const sSelect = (id, value) => { if(document.getElementById(id)) document.getElementById(id).value = value || ''; };
        const sRadio = (name, value) => { const r = document.querySelector(`input[name="${name}"][value="${value}"]`); if (r) r.checked = true; };
        
        if (!data) return;
        sSelect('age-group', data.profile.age_group); sSelect('resident-status', data.profile.resident_status);
        sFloat('salary-total', data.income.salary.salary_total); sFloat('salary-basic', data.income.salary.salary_basic); sFloat('salary-hra', data.income.salary.salary_hra);
        sFloat('hp-rent-received', data.income.house_property.hp_rent_received); sFloat('hp-municipal-taxes', data.income.house_property.hp_municipal_taxes);
        sFloat('capital-gains', data.income.capital_gains); sFloat('business-profession', data.income.business_profession);
        sFloat('other-sources', data.income.other_sources); sFloat('other-sources-interest-savings', data.income.other_sources_interest_savings);
        sFloat('rent-paid', data.deductions.hra_details.rent_paid); sRadio('is_metro', data.deductions.hra_details.is_metro.toString());
        sFloat('section-80c', data.deductions.section_80c); sFloat('section-80ccd-1b', data.deductions.section_80ccd_1b);
        sFloat('section-80d-self', data.deductions.section_80d_self); sBool('self-above-60', data.deductions.self_above_60);
        sFloat('section-80d-parents', data.deductions.section_80d_parents); sBool('parents-above-60', data.deductions.parents_above_60);
        sFloat('section-24b', data.deductions.section_24b); sFloat('section-80e', data.deductions.section_80e);
        sSelect('section-80u', data.deductions.section_80u); sSelect('section-80dd', data.deductions.section_80dd);
    };

    const loadProfileFromServer = async (email) => {
        try {
            const response = await fetch(`${API_BASE_URL}/profile/${email}`);
            if (response.ok) { const data = await response.json(); populateForm(data); }
            else if (response.status === 404) { taxForm.reset(); }
        } catch (error) { console.error("Network error:", error); alert("Could not connect to server."); }
    };
    
    // --- EVENT LISTENERS ---
    continueBtn.addEventListener('click', async () => {
        const email = userEmailLogin.value.trim();
        if (email === '' || !/^\S+@\S+\.\S+$/.test(email)) { return alert('Please enter a valid email address.'); }
        userEmailFinal.value = email;
        await loadProfileFromServer(email);
        welcomeScreen.style.display = 'none'; taxWizard.style.display = 'block'; showStep(1);
    });

    taxForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const email = userEmailFinal.value.trim();
        if (email === '' || !/^\S+@\S+\.\S+$/.test(email)) { return alert('Please confirm your email address.'); }

        resultsContainer.innerHTML = '<div class="loader"></div>';
        currentStep = 4; showStep(4);
        const dataPayload = getFormData();

        try {
            const saveResponse = await fetch(`${API_BASE_URL}/profile`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dataPayload) });
            if (!saveResponse.ok) { throw new Error(`Failed to save profile (${saveResponse.status})`); }
            
            const calcResponse = await fetch(`${API_BASE_URL}/calculate/${email}`, { method: 'POST' });
            if (!calcResponse.ok) { throw new Error(`Failed to retrieve calculation (${calcResponse.status})`); }
            
            const results = await calcResponse.json();
            displayResults(results);
        } catch (error) {
            resultsContainer.innerHTML = `<p class="error-text">An error occurred: ${error.message}. Please check logs for details.</p>`;
        }
    });

    // --- DISPLAY RESULTS (Final, Simplified Version) ---
    const formatCurrency = (num) => `₹ ${num.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

    const createResultCard = (title, data, cardClass = '') => {
        return `
            <div class="result-card ${cardClass}">
                <h3>${title}</h3>
                <table class="results-table">
                    <tr><td>Gross Income</td><td>${formatCurrency(data.gti)}</td></tr>
                    <tr><td><strong>Taxable Income</strong></td><td><strong>${formatCurrency(data.taxable_income)}</strong></td></tr>
                    <tr class="separator"><td colspan="2"><hr></td></tr>
                    <tr class="total-tax"><td><strong>Total Tax Payable</strong></td><td><strong>${formatCurrency(data.total_tax)}</strong></td></tr>
                </table>
            </div>`;
    };

    // NEW helper function to create the Savings Breakdown table
    const createSavingsBreakdown = (breakdownData) => {
        if (!breakdownData || breakdownData.length === 0) return '';
        
        const rows = breakdownData.map(item => `
            <tr>
                <td>${item.name}</td>
                <td>${formatCurrency(item.user_amount)}</td>
                <td>${formatCurrency(item.advised_amount)}</td>
            </tr>
        `).join('');

        return `
            <div class="savings-breakdown-card">
                <h3><i class="fa-solid fa-magnifying-glass-dollar"></i> Savings Breakdown</h3>
                <p>Here's a look at where the potential savings come from:</p>
                <table class="breakdown-table">
                    <thead>
                        <tr>
                            <th>Deduction</th>
                            <th>Your Input</th>
                            <th>Our Suggestion</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        `;
    };

    const displayResults = (results) => {
        const html = `
            <h2><i class="fa-solid fa-wand-magic-sparkles"></i> Your Tax Saving Potential</h2>
            <div class="results-summary">
                <p>${results.summary.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</p>
            </div>
            
            <div class="results-comparison-grid">
                ${createResultCard('Your Tax (As Entered)', results.currentTax)}
                
                ${results.potentialSavings > 0 ? `
                    <div class="savings-arrow">
                        <p>You Can Save</p>
                        <i class="fa-solid fa-arrow-right-long"></i>
                        <strong>${formatCurrency(results.potentialSavings)}</strong>
                    </div>
                ` : '<div class="savings-arrow"><i class="fa-solid fa-check-circle"></i><p>Optimized!</p></div>'}
                
                ${createResultCard('Your Potential Tax (With Advice)', results.potentialTax, 'advised-card')}
            </div>

            ${createSavingsBreakdown(results.savingsBreakdown)}

            <div class="advice-grid">
                <div class="advice-section">
                    <h3><i class="fa-solid fa-lightbulb"></i> How to Achieve These Savings</h3>
                    <ul>${results.advice.taxSavingAdvice.map(item => `<li><strong>${item.title}:</strong> ${item.details}</li>`).join('') || '<p>You are already maximizing your savings!</p>'}</ul>
                </div>
                <div class="advice-section">
                    <h3><i class="fa-solid fa-seedling"></i> Financial Wellness Advice</h3>
                    <ul>${results.advice.wellnessAdvice.map(item => `<li><strong>${item.title}:</strong> ${item.details}</li>`).join('') || '<p>Keep up the great work!</p>'}</ul>
                </div>
            </div>

            <div class="wizard-nav" style="justify-content: center; margin-top: 2rem;">
                 <button type="button" class="btn" id="start-over-btn">Start Over</button>
            </div>`;
        
        resultsContainer.innerHTML = html;
        document.getElementById('start-over-btn').addEventListener('click', () => {
            taxForm.reset(); userEmailLogin.value = ''; welcomeScreen.style.display = 'block';
            taxWizard.style.display = 'none'; currentStep = 1;
        });
    };
});