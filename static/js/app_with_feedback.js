// Legal Name Comparison System with Feedback Loop

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Global variables
let currentResults = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupFileUploads();
    setupDragAndDrop();
    loadFeedbackStats();
    loadModelVersions();
    updateSystemStatus();
});

// Setup file upload handlers
function setupFileUploads() {
    const trainingFile = document.getElementById('trainingFile');
    const predictionFile = document.getElementById('predictionFile');
    
    trainingFile.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            uploadTrainingFile(e.target.files[0]);
        }
    });
    
    predictionFile.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            uploadPredictionFile(e.target.files[0]);
        }
    });
}

// Setup drag and drop functionality
function setupDragAndDrop() {
    const trainingArea = document.getElementById('trainingUploadArea');
    const predictionArea = document.getElementById('predictionUploadArea');
    
    [trainingArea, predictionArea].forEach(area => {
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                if (this.id === 'trainingUploadArea') {
                    uploadTrainingFile(files[0]);
                } else {
                    uploadPredictionFile(files[0]);
                }
            }
        });
    });
}

// Upload training file
function uploadTrainingFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    showLoading('trainingLoading', true);
    hideResults('trainingResults');

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading('trainingLoading', false);
        
        if (data.success) {
            showTrainingResults(data);
            showAlert('Model trained successfully!', 'success');
            loadFeedbackStats();
            loadModelVersions();
        } else {
            showAlert(data.error, 'error');
        }
    })
    .catch(error => {
        showLoading('trainingLoading', false);
        showAlert('Error uploading file: ' + error.message, 'error');
    });
}

// Upload prediction file
function uploadPredictionFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    showLoading('predictionLoading', true);
    hideResults('predictionResults');

    fetch('/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading('predictionLoading', false);
        
        if (data.success) {
            showPredictionResults(data);
            showAlert('Predictions completed successfully!', 'success');
        } else {
            showAlert(data.error, 'error');
        }
    })
    .catch(error => {
        showLoading('predictionLoading', false);
        showAlert('Error processing predictions: ' + error.message, 'error');
    });
}

// Show training results
function showTrainingResults(data) {
    document.getElementById('modelAccuracy').textContent = (data.accuracy * 100).toFixed(2) + '%';
    document.getElementById('dataPairs').textContent = data.message.split(' ')[3];
    
    document.getElementById('trainingResults').style.display = 'block';
}

// Show prediction results
function showPredictionResults(data) {
    currentResults = data.results;
    
    // Update stats
    document.getElementById('totalPredictions').textContent = data.summary.total_predictions;
    document.getElementById('materialCount').textContent = data.summary.material_count;
    document.getElementById('immaterialCount').textContent = data.summary.immaterial_count;
    document.getElementById('materialPercentage').textContent = data.summary.material_percentage + '%';
    
    // Update prediction chart
    if (typeof createPredictionChart === 'function') {
        createPredictionChart(data.summary.material_count, data.summary.immaterial_count);
    }
    
    // Populate table
    const tableBody = document.getElementById('resultsTableBody');
    tableBody.innerHTML = '';
    
    data.results.forEach((result, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(result.name1)}</td>
            <td>${escapeHtml(result.name2)}</td>
            <td><span class="badge ${result.is_material ? 'bg-danger' : 'bg-success'}">${result.prediction}</span></td>
            <td>${(result.materiality_probability * 100).toFixed(1)}%</td>
            <td>${(result.immateriality_probability * 100).toFixed(1)}%</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-sm btn-success me-1" onclick="submitFeedback(${index}, true)">
                        <i class="fas fa-check"></i> Correct
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="submitFeedback(${index}, false)">
                        <i class="fas fa-times"></i> Wrong
                    </button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    document.getElementById('predictionResults').style.display = 'block';
}

// Update results table with feedback options
function updateResultsTable(results) {
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';
    
    results.forEach((result, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(result.name1)}</td>
            <td>${escapeHtml(result.name2)}</td>
            <td>
                <span class="badge ${result.is_material ? 'bg-danger' : 'bg-success'}">
                    ${result.prediction}
                </span>
            </td>
            <td>${(result.materiality_probability * 100).toFixed(2)}%</td>
            <td>${(result.immateriality_probability * 100).toFixed(2)}%</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-success btn-sm" onclick="submitFeedback(${index}, false)">
                        <i class="fas fa-check"></i> Correct
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="submitFeedback(${index}, true)">
                        <i class="fas fa-times"></i> Wrong
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Submit feedback
function submitFeedback(index, isWrong) {
    console.log('submitFeedback called:', index, isWrong);
    console.log('currentResults:', currentResults);
    
    const result = currentResults[index];
    console.log('selected result:', result);
    
    const userCorrection = isWrong ? !result.is_material : result.is_material;
    
    const feedbackData = {
        name1: result.name1,
        name2: result.name2,
        original_prediction: result.is_material,
        user_correction: userCorrection,
        confidence_score: result.materiality_probability,
        feedback_text: isWrong ? 'User marked as incorrect' : 'User confirmed as correct'
    };
    
    console.log('feedbackData:', feedbackData);
    
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedbackData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Feedback response:', data);
        if (data.success) {
            showAlert('Feedback submitted successfully!', 'success');
            if (data.model_retrained) {
                showAlert('Model has been retrained with new feedback data!', 'info');
            }
            loadFeedbackStats();
            loadModelVersions();
        } else {
            showAlert(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Feedback error:', error);
        showAlert('Error submitting feedback: ' + error.message, 'error');
    });
}

// Load feedback statistics
function loadFeedbackStats() {
    fetch('/feedback/stats')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const stats = data.stats;
            document.getElementById('feedbackStats').innerHTML = `
                <div class="mb-2">
                    <small>Total Feedback: <strong>${stats.total_feedback}</strong></small>
                </div>
                <div class="mb-2">
                    <small>Unprocessed: <strong>${stats.unprocessed_feedback}</strong></small>
                </div>
                <div class="mb-2">
                    <small>Correction Rate: <strong>${stats.correction_rate}%</strong></small>
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Error loading feedback stats:', error);
    });
}

// Load model versions
function loadModelVersions() {
    fetch('/model/versions')
    .then(response => response.json())
    .then(data => {
        if (data.success && data.versions.length > 0) {
            const versions = data.versions;
            const latest = versions[0];
            
            document.getElementById('modelVersions').innerHTML = `
                <div class="mb-2">
                    <small>Latest: <strong>${latest.version}</strong></small>
                </div>
                <div class="mb-2">
                    <small>Accuracy: <strong>${(latest.accuracy * 100).toFixed(2)}%</strong></small>
                </div>
                <div class="mb-2">
                    <small>Total Versions: <strong>${versions.length}</strong></small>
                </div>
            `;
        } else {
            document.getElementById('modelVersions').innerHTML = '<small>No models trained yet</small>';
        }
    })
    .catch(error => {
        console.error('Error loading model versions:', error);
    });
}

// Manual retrain
function manualRetrain() {
    if (confirm('Are you sure you want to manually retrain the model with available feedback data?')) {
        fetch('/model/retrain', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Model retrained successfully!', 'success');
                loadFeedbackStats();
                loadModelVersions();
            } else {
                showAlert(data.message, 'warning');
            }
        })
        .catch(error => {
            showAlert('Error retraining model: ' + error.message, 'error');
        });
    }
}

// Update system status
function updateSystemStatus() {
    fetch('/health')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'healthy') {
            document.getElementById('systemStatus').innerHTML = '<span class="badge bg-success">Healthy</span>';
        } else {
            document.getElementById('systemStatus').innerHTML = '<span class="badge bg-danger">Unhealthy</span>';
        }
    })
    .catch(error => {
        document.getElementById('systemStatus').innerHTML = '<span class="badge bg-danger">Error</span>';
    });
}

// Utility functions
function showLoading(elementId, show) {
    const element = document.getElementById(elementId);
    if (show) {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

function hideResults(elementId) {
    const element = document.getElementById(elementId);
    element.style.display = 'none';
}

function showAlert(message, type) {
    console.log('showAlert called:', message, type);
    
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        console.error('alertContainer not found!');
        return;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <strong>${type.toUpperCase()}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    console.log('Alert added to DOM');
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Test prediction function
function testPrediction() {
    console.log('testPrediction function called');
    
    // Test if elements exist
    const name1Element = document.getElementById('name1');
    const name2Element = document.getElementById('name2');
    
    console.log('name1Element:', name1Element);
    console.log('name2Element:', name2Element);
    
    if (!name1Element || !name2Element) {
        console.error('Could not find name input elements');
        showAlert('Error: Could not find input elements', 'error');
        return;
    }
    
    const name1 = name1Element.value;
    const name2 = name2Element.value;
    
    console.log('Name1:', name1);
    console.log('Name2:', name2);
    
    if (!name1 || !name2) {
        showAlert('Please enter both names', 'warning');
        return;
    }
    
    // Show loading
    showLoading('testLoading', true);
    hideResults('testResult');
    
    console.log('Sending request to /test_prediction');
    
    // First check if we have a trained model
    fetch('/model/versions')
    .then(response => {
        console.log('Model versions response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Model versions data:', data);
        if (!data.versions || data.versions.length === 0) {
            showAlert('No trained model available. Please train a model first.', 'warning');
            return Promise.reject('No model available');
        }
        
        // Send single prediction request
        return fetch('/test_prediction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name1: name1,
                name2: name2
            })
        });
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        showLoading('testLoading', false);
        
        if (data.success) {
            const result = data.result;
            const isMaterial = result.is_material;
            const materialityProb = (result.materiality_probability * 100).toFixed(1);
            const immaterialityProb = (result.immateriality_probability * 100).toFixed(1);
            const confidence = Math.max(result.materiality_probability, result.immateriality_probability) * 100;
            
            // Update result display
            document.getElementById('testPrediction').textContent = isMaterial ? 'MATERIAL CHANGE' : 'IMMATERIAL CHANGE';
            document.getElementById('testPrediction').className = isMaterial ? 'text-danger' : 'text-success';
            document.getElementById('testConfidence').textContent = confidence.toFixed(1) + '%';
            document.getElementById('materialityProb').textContent = materialityProb;
            document.getElementById('immaterialityProb').textContent = immaterialityProb;
            
            // Update progress bar
            const progressBar = document.getElementById('confidenceBar');
            progressBar.style.width = confidence + '%';
            progressBar.className = `progress-bar ${confidence > 80 ? 'bg-success' : confidence > 60 ? 'bg-warning' : 'bg-danger'}`;
            
            // Show result
            document.getElementById('testResult').style.display = 'block';
        } else {
            showAlert(data.error || 'Error making prediction', 'error');
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        showLoading('testLoading', false);
        showAlert('Error making prediction: ' + error.message, 'error');
    });
} 