document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if elements exist
    initCharts();
    
    // Handle forecast generation if on the forecast page
    initForecastPage();
    
    // Initialize receipt extractor if on the receipt extractor page
    if (document.getElementById('receipt-uploader')) {
        // Only initialize once
        if (!window.receiptExtractorInitialized) {
            initReceiptExtractor();
            window.receiptExtractorInitialized = true;
        }
    }
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

// Initialize receipt extractor functionality
function initReceiptExtractor() {
    // Elements
    const landingView = document.getElementById('landing-view');
    const previewView = document.getElementById('preview-view');
    const loadingView = document.getElementById('loading-view');
    const resultsView = document.getElementById('results-view');
    const errorView = document.getElementById('error-view');
    
    const chooseFileBtn = document.getElementById('choose-file-btn');
    const fileInput = document.getElementById('receipt-file-input');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const extractBtn = document.getElementById('extract-btn');
    const startOverBtn = document.getElementById('start-over-btn');
    const errorRetryBtn = document.getElementById('error-retry-btn');
    
    const selectedFilename = document.getElementById('selected-filename');
    const selectedFileInfo = document.getElementById('selected-fileinfo');
    
    // Selected file storage
    let selectedFile = null;
    
    // Show a specific view and hide others
    function showView(viewElement) {
        // Hide all views
        landingView.style.display = 'none';
        previewView.style.display = 'none';
        loadingView.style.display = 'none';
        resultsView.style.display = 'none';
        errorView.style.display = 'none';
        
        // Show the specified view
        if (viewElement) {
            viewElement.style.display = 'block';
        }
    }
    
    // File selection via button
    chooseFileBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        handleFileSelection(e.target.files[0]);
    });
    
    // Handle file selection
    function handleFileSelection(file) {
        if (!file) return;
        
        // Check file type
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (!['jpg', 'jpeg', 'png'].includes(fileExtension)) {
            document.getElementById('error-message').textContent = 'Invalid file type. Only JPG, JPEG, and PNG files are allowed.';
            showView(errorView);
            return;
        }
        
        // Store selected file
        selectedFile = file;
        
        // Update preview information
        selectedFilename.textContent = file.name;
        
        // Format file info with current date and time
        const now = new Date();
        const formattedDate = now.toLocaleDateString();
        const formattedTime = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        selectedFileInfo.textContent = `Uploaded by User, Uploaded on ${formattedDate} at ${formattedTime}`;
        
        // Show preview view
        showView(previewView);
    }
    
    // Drag and drop functionality
    const uploadArea = landingView.querySelector('.upload-area');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadArea.classList.add('border', 'border-primary');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('border', 'border-primary');
    }
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        // Prevent default behavior and stop propagation
        e.preventDefault();
        e.stopPropagation();
        
        const dt = e.dataTransfer;
        const file = dt.files[0];
        handleFileSelection(file);
    }
    
    // Remove selected file
    removeFileBtn.addEventListener('click', function() {
        selectedFile = null;
        fileInput.value = '';
        showView(landingView);
    });
    
    // Extract receipt contents
    extractBtn.addEventListener('click', function(e) {
        // Prevent any default action or event bubbling
        e.preventDefault();
        e.stopPropagation();
        
        if (!selectedFile) return;
        
        // Show loading view
        showView(loadingView);
        
        // Create form data for upload
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        // Call API to extract receipt details
        fetch('/api/extract-receipt-details', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayExtractionResults(data.data);
            } else {
                throw new Error(data.message || 'Error processing receipt');
            }
        })
        .catch(error => {
            document.getElementById('error-message').textContent = error.message;
            showView(errorView);
        });
    });
    
    // Display extraction results
    function displayExtractionResults(data) {
        try {
            // Ensure data has all required fields with defaults
            data = {
                image_url: data.image_url || '',
                vendor_name: data.vendor_name || 'Unknown Vendor',
                date: data.date || '',
                currency: data.currency || 'USD',
                receipt_items: Array.isArray(data.receipt_items) ? data.receipt_items : [],
                tax: typeof data.tax === 'number' ? data.tax : 0,
                total: typeof data.total === 'number' ? data.total : 0
            };
            
            // Set receipt image
            document.getElementById('receipt-image-result').src = data.image_url;
            
            // Set receipt details
            document.getElementById('vendor-name').textContent = data.vendor_name;
            document.getElementById('receipt-date').textContent = formatDate(data.date);
            document.getElementById('receipt-currency').textContent = data.currency;
            
            // Set receipt items
            const itemsContainer = document.getElementById('receipt-items');
            itemsContainer.innerHTML = '';
            
            if (data.receipt_items.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="2" class="text-center">No items found</td>';
                itemsContainer.appendChild(row);
            } else {
                data.receipt_items.forEach(item => {
                    const itemName = item.item_name || 'Unnamed Item';
                    const itemCost = typeof item.item_cost === 'number' ? item.item_cost : 0;
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${itemName}</td>
                        <td class="text-end">$${itemCost.toFixed(2)}</td>
                    `;
                    itemsContainer.appendChild(row);
                });
            }
            
            // Set tax and total
            document.getElementById('receipt-tax').textContent = `$${data.tax.toFixed(2)}`;
            document.getElementById('receipt-total').textContent = `$${data.total.toFixed(2)}`;
            
            // Show results view
            showView(resultsView);
        } catch (error) {
            console.error('Error displaying extraction results:', error);
            document.getElementById('error-message').textContent = 'Error displaying extraction results';
            showView(errorView);
        }
    }
    
    // Format date from YYYY-MM-DD to readable format
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        try {
            const [year, month, day] = dateString.split('-');
            const date = new Date(year, month - 1, day);
            return date.toLocaleDateString(undefined, options);
        } catch (e) {
            return dateString;
        }
    }
    
    // Start over button
    startOverBtn.addEventListener('click', function() {
        selectedFile = null;
        fileInput.value = '';
        showView(landingView);
    });
    
    // Error retry button
    errorRetryBtn.addEventListener('click', function() {
        showView(landingView);
    });
} 