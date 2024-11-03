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
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [
                    sentimentScores.pos,
                    sentimentScores.neu,
                    sentimentScores.neg
                ],
                backgroundColor: [
                    '#48BB78',
                    '#CBD5E0',
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

function displayStats(stats) {
    const statsContainer = document.getElementById('textStats');
    statsContainer.innerHTML = `
        <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
            <span class="text-gray-600">Words</span>
            <span class="font-semibold">${formatNumber(stats.word_count)}</span>
        </div>
        <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
            <span class="text-gray-600">Sentences</span>
            <span class="font-semibold">${stats.sentence_count}</span>
        </div>
        <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
            <span class="text-gray-600">Reading Time</span>
            <span class="font-semibold">${stats.reading_time} min</span>
        </div>
        <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
            <span class="text-gray-600">Complexity Score</span>
            <span class="font-semibold">${stats.complexity_score}/10</span>
        </div>
    `;
}

function displayTopics(topics) {
    const topicsContainer = document.getElementById('topicsList');
    topicsContainer.innerHTML = topics
        .map(topic => `<span class="topic-tag">${topic}</span>`)
        .join('');
}

function displayKeyPhrases(phrases) {
    const phrasesContainer = document.getElementById('phrasesList');
    phrasesContainer.innerHTML = phrases
        .map(phrase => `<div class="text-gray-700 mb-1">• ${phrase}</div>`)
        .join('');
}

function updateHistoryChart(history) {
    const ctx = document.getElementById('historyChart').getContext('2d');
    
    if (historyChart) {
        historyChart.destroy();
    }

    const dates = history.map(item => item.timestamp);
    const compressionRatios = history.map(item => item.compression_ratio);

    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Compression Ratio (%)',
                data: compressionRatios,
                borderColor: '#4299E1',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
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
            displayStats(data.analysis.stats);
            displayTopics(data.analysis.topics);
            displayKeyPhrases(data.analysis.key_phrases);
            
            // Display summaries
            document.getElementById('headline').textContent = data.summary_formats.headline;
            document.getElementById('standard').textContent = data.summary_formats.standard;
            document.getElementById('socialText').textContent = data.summary_formats.social_post;
            document.getElementById('charCount').textContent = 
                `${data.summary_formats.social_post.length}/280 characters`;
            
            // Display bullet points
            const bulletsList = document.getElementById('bullets');
            bulletsList.innerHTML = data.summary_formats.bullet_points
                .map(point => `<li class="mb-2">${point}</li>`)
                .join('');
            
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