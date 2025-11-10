const API_KEY = 'dev-key-12345';
const API_URL = 'http://localhost:8000/api/v1';

const predictionHistory = [];

function initializePCAInputs() {
    const pcaGrid = document.getElementById('pcaGrid');
    for (let i = 1; i <= 28; i++) {
        const div = document.createElement('div');
        div.className = 'pca-input';
        div.innerHTML = `
            <label for="v${i}">V${i}</label>
            <input type="number" id="v${i}" step="any" placeholder="0.0" value="0.0" required>
        `;
        pcaGrid.appendChild(div);
    }
}

function loadSampleData() {
    const sampleTransaction = {
        transactionId: `SAMPLE-${Date.now()}`,
        amount: 149.62,
        time: 406,
        features: {
            V1: -1.3598071336738,
            V2: -0.0727811733098497,
            V3: 2.53634673796914,
            V4: 1.37815522427443,
            V5: -0.338320769942518,
            V6: 0.462387777762292,
            V7: 0.239598554061257,
            V8: 0.0986979012610507,
            V9: 0.363786969611213,
            V10: 0.0907941719789316,
            V11: -0.551599533260813,
            V12: -0.617800855762348,
            V13: -0.991389847235408,
            V14: -0.311169353699879,
            V15: 1.46817697209427,
            V16: -0.470400525259478,
            V17: 0.207971241929242,
            V18: 0.0257905801985591,
            V19: 0.403992960255733,
            V20: 0.251412098239705,
            V21: -0.018306777944153,
            V22: 0.277837575558899,
            V23: -0.110473910188767,
            V24: 0.0669280749146731,
            V25: 0.128539358273528,
            V26: -0.189114843888824,
            V27: 0.133558376740387,
            V28: -0.0210530534538215
        }
    };

    document.getElementById('transactionId').value = sampleTransaction.transactionId;
    document.getElementById('amount').value = sampleTransaction.amount;
    document.getElementById('time').value = sampleTransaction.time;

    for (let i = 1; i <= 28; i++) {
        document.getElementById(`v${i}`).value = sampleTransaction.features[`V${i}`];
    }
}

async function submitPrediction(event) {
    event.preventDefault();

    const transactionId = document.getElementById('transactionId').value;
    const amount = parseFloat(document.getElementById('amount').value);
    const time = parseFloat(document.getElementById('time').value);

    const transaction = {
        Time: time,
        Amount: amount
    };

    for (let i = 1; i <= 28; i++) {
        transaction[`V${i}`] = parseFloat(document.getElementById(`v${i}`).value);
    }

    const payload = {
        transaction_id: transactionId,
        transaction: transaction
    };

    showLoading();

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResult(result);
        addToHistory(result);
    } catch (error) {
        displayError(error.message);
    }
}

function showLoading() {
    const container = document.getElementById('resultContainer');
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p style="margin-top: 15px; color: #666;">Analyzing transaction...</p>
        </div>
    `;
}

function displayResult(result) {
    const container = document.getElementById('resultContainer');
    
    const isFraud = result.prediction === 1;
    const fraudClass = isFraud ? 'fraud' : 'legitimate';
    const fraudText = isFraud ? 'FRAUD DETECTED' : 'LEGITIMATE';
    
    container.innerHTML = `
        <div class="result-card">
            <div class="result-header">
                <h3>Transaction: ${result.transaction_id}</h3>
                <span class="result-badge badge-${fraudClass}">${fraudText}</span>
            </div>
            
            <div class="result-metrics">
                <div class="metric">
                    <div class="metric-label">Fraud Probability</div>
                    <div class="metric-value">${(result.fraud_probability * 100).toFixed(2)}%</div>
                </div>
                
                <div class="metric risk-${result.risk_level}">
                    <div class="metric-label">Risk Level</div>
                    <div class="metric-value">${result.risk_level}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-label">Anomaly Score</div>
                    <div class="metric-value">${result.anomaly_score.toFixed(4)}</div>
                </div>
                
                <div class="metric">
                    <div class="metric-label">Threshold</div>
                    <div class="metric-value">${result.threshold.toFixed(4)}</div>
                </div>
            </div>
            
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 0.85em; color: #666;">
                Model Version: ${result.model_version} | ${new Date(result.timestamp).toLocaleString()}
            </div>
        </div>
    `;
}

function displayError(message) {
    const container = document.getElementById('resultContainer');
    container.innerHTML = `
        <div class="error-message">
            <strong>Error:</strong> ${message}
        </div>
        <p class="placeholder">Please check your input and try again</p>
    `;
}

function addToHistory(result) {
    predictionHistory.unshift(result);
    
    if (predictionHistory.length > 10) {
        predictionHistory.pop();
    }
    
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
    const container = document.getElementById('historyContainer');
    
    if (predictionHistory.length === 0) {
        container.innerHTML = '<p class="placeholder">No predictions yet</p>';
        return;
    }
    
    container.innerHTML = predictionHistory.map(item => {
        const isFraud = item.prediction === 1;
        const badgeClass = isFraud ? 'fraud' : 'legitimate';
        const badgeText = isFraud ? 'FRAUD' : 'LEGIT';
        
        return `
            <div class="history-item">
                <div class="history-info">
                    <h4>${item.transaction_id}</h4>
                    <p>Probability: ${(item.fraud_probability * 100).toFixed(2)}% | Risk: ${item.risk_level}</p>
                </div>
                <span class="result-badge badge-${badgeClass}">${badgeText}</span>
            </div>
        `;
    }).join('');
}

document.addEventListener('DOMContentLoaded', () => {
    initializePCAInputs();
    document.getElementById('predictionForm').addEventListener('submit', submitPrediction);
});
