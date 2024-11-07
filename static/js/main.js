let sentimentChart = null;
let historyChart = null;

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function createSentimentChart(sentimentScores) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    if (sentimentChart) {
        sentimentChart.destroy();
    }

    sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative'],
            datasets: [{
                data: [
                    sentimentScores.pos,
                    
                    sentimentScores.neg
                ],
                backgroundColor: [
                    '#48BB78',
                    
                    '#F56565'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}







function copyText(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = 'Copy', 2000);
    });
}

document.getElementById('summarizeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData();
    
    // Get form values
    formData.append('text', form.text.value);
    formData.append('min_length', form.min_length.value);
    formData.append('max_length', form.max_length.value);
    formData.append('language', form.language.value);
    document.getElementById('results').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');
    
    try {
        const response = await fetch('/summarize', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display analysis
            createSentimentChart(data.analysis.sentiment.scores);
            
            
            // Display summaries
            
            document.getElementById('standard').textContent = data.summary_formats.standard;
           
            
            // Display bullet points
            
            
            document.getElementById('results').classList.remove('hidden');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
});

document.getElementById('historyButton').addEventListener('click', async () => {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (data.success) {
            updateHistoryChart(data.history);
            document.getElementById('historyModal').classList.remove('hidden');
        } else {
            alert('Error loading history: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

document.getElementById('closeHistory').addEventListener('click', () => {
    document.getElementById('historyModal').classList.add('hidden');
});

// Close modal when clicking outside
document.getElementById('historyModal').addEventListener('click', (e) => {
    if (e.target.id === 'historyModal') {
        document.getElementById('historyModal').classList.add('hidden');
    }
});

// Add validation for min/max length
document.getElementById('min_length').addEventListener('change', function() {
    const min = parseInt(this.value);
    const max = parseInt(document.getElementById('max_length').value);
    if (min >= max) {
        this.value = max - 10;
        alert('Minimum length must be less than maximum length');
    }
});

document.getElementById('max_length').addEventListener('change', function() {
    const max = parseInt(this.value);
    const min = parseInt(document.getElementById('min_length').value);
    if (max <= min) {
        this.value = min + 10;
        alert('Maximum length must be greater than minimum length');
    }
});
