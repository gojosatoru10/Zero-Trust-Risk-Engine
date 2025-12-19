async function checkRisk() {
    const btn = document.getElementById('analyzeBtn');
    const originalText = btn.innerHTML;
    
    // 1. Show Loading State
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Scanning...';
    
    // 2. Hide previous results
    const resultCard = document.getElementById('result-card');
    resultCard.style.display = 'none';

    // 3. Gather Data
    const payload = {
        Category: document.getElementById('Category').value,
        MitreTechniques: document.getElementById('MitreTechniques').value,
        ActionGrouped: document.getElementById('ActionGrouped').value,
        EntityType: document.getElementById('EntityType').value,
        OSFamily: document.getElementById('OSFamily').value,
        SuspicionLevel: document.getElementById('SuspicionLevel').value,
        CountryCode: document.getElementById('CountryCode').value
    };

    try {
        // 4. Call the API
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        // 5. Handle Logic (Even if 403 Forbidden, we want to show the GUI result)
        let decision, grade, conf, breakdown;

        if (response.status === 403) {
            // It was blocked, but we parse the "detail" to get the stats
            decision = data.detail.decision;
            grade = data.detail.predicted_grade;
            conf = data.detail.confidence;
            breakdown = data.detail.breakdown;
        } else if (response.ok) {
            decision = data.decision;
            grade = data.predicted_grade;
            conf = data.confidence;
            breakdown = data.breakdown;
        } else {
            alert("Error communicating with server.");
            return;
        }

        // 6. Update UI
        displayResult(decision, grade, conf, breakdown);

    } catch (error) {
        console.error("Error:", error);
        alert("Failed to connect to the Zero Trust Engine.");
    } finally {
        // Reset Button
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

function displayResult(decision, grade, conf, breakdown) {
    const resultCard = document.getElementById('result-card');
    const iconContainer = document.getElementById('icon-container');
    const decisionText = document.getElementById('decision-text');
    const gradeText = document.getElementById('grade-text');
    const probBar = document.getElementById('prob-bar');
    const breakdownList = document.getElementById('breakdown-list');

    resultCard.style.display = 'block';
    breakdownList.innerHTML = ''; // Clear old list

    const percentage = (conf * 100).toFixed(1) + "%";
    probBar.style.width = percentage;
    probBar.innerText = percentage;

    if (decision === "DENIED") {
        resultCard.className = "card mt-4 shadow-lg access-denied";
        iconContainer.innerHTML = '<i class="fas fa-ban result-icon-lg text-danger"></i>';
        decisionText.innerText = "⛔ ACCESS DENIED";
        decisionText.className = "fw-bold text-danger";
        probBar.className = "progress-bar bg-danger";
    } else {
        resultCard.className = "card mt-4 shadow-lg access-allowed";
        iconContainer.innerHTML = '<i class="fas fa-check-circle result-icon-lg text-success"></i>';
        decisionText.innerText = "✅ ACCESS GRANTED";
        decisionText.className = "fw-bold text-success";
        probBar.className = "progress-bar bg-success";
    }

    gradeText.innerText = `Reason: Predicted as ${grade}`;

    // Populate Breakdown List
    for (const [key, value] of Object.entries(breakdown)) {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${key}:</strong> ${(value * 100).toFixed(2)}%`;
        breakdownList.appendChild(li);
    }
}