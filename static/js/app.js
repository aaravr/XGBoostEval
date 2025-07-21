// Global variables
let currentResults = [];

// File upload handlers
document.addEventListener('DOMContentLoaded', function() {
    setupFileUploads();
    setupDragAndDrop();
});

function setupFileUploads() {
    // Training file upload
    document.getElementById('trainingFile').addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            uploadTrainingFile(e.target.files[0]);
        }
    });

    // Prediction file upload
    document.getElementById('predictionFile').addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            uploadPredictionFile(e.target.files[0]);
        }
    });
}

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
                const file = files[0];
                if (file.name.match(/\.(xlsx|xls)$/)) {
                    if (this.id === 'trainingUploadArea') {
                        uploadTrainingFile(file);
                    } else {
                        uploadPredictionFile(file);
                    }
                } else {
                    showAlert('Please upload an Excel file (.xlsx or .xls)', 'error');
                }
            }
        });

        area.addEventListener('click', function() {
            const input = this.querySelector('input[type="file"]');
            if (input) {
                input.click();
            }
        });
    });
}

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
        } else {
            showAlert(data.error, 'error');
        }
    })
    .catch(error => {
        showLoading('trainingLoading', false);
        showAlert('Error uploading file: ' + error.message, 'error');
    });
}

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

function showTrainingResults(data) {
    document.getElementById('modelAccuracy').textContent = (data.accuracy * 100).toFixed(2) + '%';
    document.getElementById('dataPairs').textContent = data.message.split(' ')[3];
    
    if (data.feature_plot) {
        const plotData = JSON.parse(data.feature_plot);
        Plotly.newPlot('featureImportancePlot', plotData.data, plotData.layout);
    }
    
    document.getElementById('trainingResults').style.display = 'block';
}

function showPredictionResults(data) {
    currentResults = data.results;
    
    // Update summary
    document.getElementById('totalPredictions').textContent = data.summary.total_predictions;
    document.getElementById('materialCount').textContent = data.summary.material_count;
    document.getElementById('immaterialCount').textContent = data.summary.immaterial_count;
    document.getElementById('materialPercentage').textContent = data.summary.material_percentage + '%';
    
    // Update download link
    document.getElementById('downloadResults').href = data.download_url;
    
    // Show prediction plot
    if (data.prediction_plot) {
        const plotData = JSON.parse(data.prediction_plot);
        Plotly.newPlot('predictionPlot', plotData.data, plotData.layout);
    }
    
    // Update results table
    updateResultsTable(data.results);
    
    document.getElementById('predictionResults').style.display = 'block';
}

function updateResultsTable(results) {
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';
    
    results.forEach(result => {
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
        `;
        tbody.appendChild(row);
    });
}

function testPrediction() {
    const name1 = document.getElementById('name1').value.trim();
    const name2 = document.getElementById('name2').value.trim();
    
    if (!name1 || !name2) {
        showAlert('Please enter both names', 'error');
        return;
    }
    
    showLoading('testLoading', true);
    hideResults('testResult');
    
    fetch('/test_prediction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name1: name1,
            name2: name2
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading('testLoading', false);
        
        if (data.success) {
            showTestResult(data.result);
        } else {
            showAlert(data.error, 'error');
        }
    })
    .catch(error => {
        showLoading('testLoading', false);
        showAlert('Error testing prediction: ' + error.message, 'error');
    });
}

function showTestResult(result) {
    const prediction = result.is_material ? 'Material Change' : 'Immaterial Change';
    const confidence = Math.max(result.materiality_probability, result.immateriality_probability);
    const confidencePercent = (confidence * 100).toFixed(1);
    
    document.getElementById('testPrediction').textContent = prediction;
    document.getElementById('testConfidence').textContent = confidencePercent + '%';
    document.getElementById('materialityProb').textContent = (result.materiality_probability * 100).toFixed(1);
    document.getElementById('immaterialityProb').textContent = (result.immateriality_probability * 100).toFixed(1);
    
    // Update progress bar
    const progressBar = document.getElementById('confidenceBar');
    progressBar.style.width = confidencePercent + '%';
    progressBar.style.backgroundColor = result.is_material ? '#ff7f0e' : '#1f77b4';
    
    document.getElementById('testResult').style.display = 'block';
}

function showLoading(elementId, show) {
    const element = document.getElementById(elementId);
    if (show) {
        element.classList.add('show');
    } else {
        element.classList.remove('show');
    }
}

function hideResults(elementId) {
    document.getElementById(elementId).style.display = 'none';
}

function showAlert(message, type) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Example data structure for training file
function createSampleTrainingFile() {
    const sampleData = {
        source1: ['ABC LTD', 'ABC Limited', 'XYZ Corporation'],
        source2: ['ABC Limited', 'ABC Ltd', 'XYZ Corp'],
        source3: ['ABC LLC', 'ABC Limited', 'XYZ Inc'],
        is_material: [0, 0, 0]  // 0 = immaterial, 1 = material
    };
    
    // This would be used to create a downloadable sample file
    return sampleData;
}

// Example data structure for prediction file
function createSamplePredictionFile() {
    const sampleData = {
        name1: ['ABC LTD', 'ABC Limited', 'XYZ Corporation'],
        name2: ['ABC Limited', 'XYZ Limited', 'XYZ Corp']
    };
    
    return sampleData;
} 