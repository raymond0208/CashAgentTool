document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if elements exist
    initCharts();
    
    // Handle forecast generation if on the forecast page
    initForecastPage();
});

// Initialize dashboard charts
function initCharts() {
    // Revenue Overview Chart
    if (document.getElementById('revenueChart')) {
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        const revenueChart = new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [
                    {
                        label: 'Revenue',
                        data: [3000, 6500, 6000, 8000, 9500, 12000],
                        backgroundColor: 'rgba(13, 110, 253, 0.2)',
                        borderColor: 'rgba(13, 110, 253, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Expenses',
                        data: [2000, 4000, 3800, 5500, 6500, 7500],
                        backgroundColor: 'rgba(123, 128, 254, 0.2)',
                        borderColor: 'rgba(123, 128, 254, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    // Expense Breakdown Chart
    if (document.getElementById('expenseChart')) {
        const expenseCtx = document.getElementById('expenseChart').getContext('2d');
        const expenseChart = new Chart(expenseCtx, {
            type: 'doughnut',
            data: {
                labels: ['Operations', 'Marketing', 'Payroll', 'Equipment', 'Other'],
                datasets: [{
                    data: [35, 25, 20, 10, 10],
                    backgroundColor: [
                        'rgba(13, 202, 240, 1)',
                        'rgba(123, 128, 254, 1)',
                        'rgba(255, 145, 26, 1)',
                        'rgba(25, 135, 84, 1)',
                        'rgba(108, 117, 125, 1)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                cutout: '65%'
            }
        });
    }
    
    // Cash Flow Forecast Chart
    if (document.getElementById('cashFlowChart')) {
        const cashFlowCtx = document.getElementById('cashFlowChart').getContext('2d');
        const cashFlowChart = new Chart(cashFlowCtx, {
            type: 'bar',
            data: {
                labels: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Actual',
                        data: [11000, 13000],
                        backgroundColor: 'rgba(13, 110, 253, 1)',
                        borderRadius: 4
                    },
                    {
                        label: 'Projected',
                        data: [null, null, 14000, 16000, 19000, 22000],
                        backgroundColor: 'rgba(13, 110, 253, 0.4)',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                if (value === 0) return '$0';
                                return '$' + (value >= 1000 ? (value/1000) + 'k' : value);
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

// Initialize forecast page functionality
function initForecastPage() {
    // Add event listeners to forecast buttons with data-forecast-days attribute
    document.querySelectorAll('[data-forecast-days]').forEach(button => {
        const days = button.getAttribute('data-forecast-days');
        button.addEventListener('click', () => generateForecast(days));
    });
    
    // Add event listener for "Generate All Forecasts" button
    const allForecastsButton = document.getElementById('generate-all-forecasts');
    if (allForecastsButton) {
        allForecastsButton.addEventListener('click', generateAllForecasts);
    }
    
    // Add AI assistant functionality
    const aiInput = document.querySelector('.ai-input');
    const aiSubmit = document.querySelector('.ai-submit');
    
    if (aiInput && aiSubmit) {
        // Handle submit button click
        aiSubmit.addEventListener('click', () => {
            handleAiQuery(aiInput.value);
        });
        
        // Handle Enter key press
        aiInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleAiQuery(aiInput.value);
            }
        });
    }
}

// Handle AI assistant query
function handleAiQuery(query) {
    if (!query.trim()) return;
    
    const aiAssistant = document.querySelector('.ai-assistant');
    if (!aiAssistant) return;
    
    // Clear input
    document.querySelector('.ai-input').value = '';
    
    // Add user query to the message area
    const userQuery = document.createElement('div');
    userQuery.className = 'mb-3';
    userQuery.innerHTML = `
        <div class="fw-bold">You:</div>
        <div>${query}</div>
    `;
    aiAssistant.insertBefore(userQuery, document.querySelector('.ai-input-container'));
    
    // In a real app, here you would call your AI API
    // For now, just show a placeholder response
    setTimeout(() => {
        const aiResponse = document.createElement('div');
        aiResponse.className = 'ai-assistant-message';
        aiResponse.innerHTML = `
            <div class="fw-bold">Finance Assistant:</div>
            <div>I'm analyzing your financial data based on your question: "${query}"</div>
            <div class="mt-2">This is a placeholder response. In the real app, this would be connected to your AI backend.</div>
        `;
        aiAssistant.insertBefore(aiResponse, document.querySelector('.ai-input-container'));
    }, 1000);
}

// Function to format the forecast result
function formatForecast(forecast) {
    if (!forecast || forecast.error) {
        return `<div class="alert alert-danger">Error: ${forecast.error || 'Unknown error'}</div>`;
    }
    
    const metadata = forecast.metadata || {};
    let html = `
        <div class="card mb-3">
            <div class="card-header bg-light">
                <strong>Forecast Period:</strong> ${metadata.forecast_start || 'N/A'} to ${metadata.forecast_end || 'N/A'}
                <br>
                <strong>Current Balance:</strong> $${metadata.current_balance ? metadata.current_balance.toFixed(2) : 'N/A'}
            </div>
            <div class="card-body">
                <pre class="forecast-text">${forecast.forecast_text}</pre>
            </div>
        </div>
    `;
    
    return html;
}

// Function to generate a forecast for a specific period
async function generateForecast(days) {
    const loadingElement = document.getElementById(`loading-${days}`);
    const resultElement = document.getElementById(`forecast-result-${days}`);
    
    if (!loadingElement || !resultElement) return;
    
    // Show loading indicator
    loadingElement.classList.remove('d-none');
    resultElement.innerHTML = '';
    
    try {
        const response = await fetch(`/api/forecast/${days}`);
        const data = await response.json();
        
        // Format and display the result
        resultElement.innerHTML = formatForecast(data);
    } catch (error) {
        resultElement.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    } finally {
        // Hide loading indicator
        loadingElement.classList.add('d-none');
    }
}

// Function to generate all forecasts
async function generateAllForecasts() {
    const loadingElement = document.getElementById('loading-all');
    const resultElement = document.getElementById('all-forecasts-result');
    
    if (!loadingElement || !resultElement) return;
    
    // Show loading indicator
    loadingElement.classList.remove('d-none');
    resultElement.innerHTML = '';
    
    try {
        const response = await fetch('/api/forecast/all');
        const data = await response.json();
        
        // Format and display all results
        let html = '<div class="accordion" id="forecastAccordion">';
        
        // 30-day forecast
        html += `
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading30">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse30">
                        30-Day Forecast
                    </button>
                </h2>
                <div id="collapse30" class="accordion-collapse collapse show" aria-labelledby="heading30" data-bs-parent="#forecastAccordion">
                    <div class="accordion-body">
                        ${formatForecast(data['30_days'])}
                    </div>
                </div>
            </div>
        `;
        
        // 90-day forecast
        html += `
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading90">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse90">
                        90-Day Forecast
                    </button>
                </h2>
                <div id="collapse90" class="accordion-collapse collapse" aria-labelledby="heading90" data-bs-parent="#forecastAccordion">
                    <div class="accordion-body">
                        ${formatForecast(data['90_days'])}
                    </div>
                </div>
            </div>
        `;
        
        // 180-day forecast
        html += `
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading180">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse180">
                        180-Day Forecast
                    </button>
                </h2>
                <div id="collapse180" class="accordion-collapse collapse" aria-labelledby="heading180" data-bs-parent="#forecastAccordion">
                    <div class="accordion-body">
                        ${formatForecast(data['180_days'])}
                    </div>
                </div>
            </div>
        `;
        
        html += '</div>';
        resultElement.innerHTML = html;
    } catch (error) {
        resultElement.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    } finally {
        // Hide loading indicator
        loadingElement.classList.add('d-none');
    }
} 