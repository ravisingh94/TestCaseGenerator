const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const featureNameInput = document.getElementById('feature-name');
const generateBtn = document.getElementById('generate-btn');
const resultsSection = document.getElementById('results-section');
const testCasesContainer = document.getElementById('test-cases-container');
const hallucinationReport = document.getElementById('hallucination-report');
const hallucinationList = document.getElementById('hallucination-list');
const hallucinationBadge = document.getElementById('hallucination-badge');
const exportBtn = document.getElementById('export-btn');
const exportMenu = document.getElementById('export-menu');

let uploadedFilePath = null;
window.generatedTestCases = []; // Store test cases for export (globally accessible)

// Drag & Drop Events
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Show uploading state
    fileInfo.textContent = `Uploading ${file.name}...`;
    fileInfo.classList.remove('hidden');

    fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            uploadedFilePath = data.file_path;
            fileInfo.textContent = `Uploaded: ${data.filename}`;
            checkEnableGenerate();
        })
        .catch(error => {
            console.error('Error:', error);
            fileInfo.textContent = 'Upload failed';
        });
}

const urlInput = document.getElementById('url-input');

urlInput.addEventListener('input', () => {
    if (urlInput.value.trim() !== '') {
        // Disable file input if URL is entered
        dropZone.classList.add('disabled');
        document.getElementById('file-input').disabled = true;
        uploadedFilePath = null;
        fileInfo.textContent = '';
        fileInfo.classList.add('hidden');
    } else {
        dropZone.classList.remove('disabled');
        document.getElementById('file-input').disabled = false;
    }
    checkEnableGenerate();
});

// Add event listener for feature name input
featureNameInput.addEventListener('input', checkEnableGenerate);

function checkEnableGenerate() {
    const hasFile = uploadedFilePath !== null;
    const hasUrl = urlInput.value.trim() !== '';
    const hasFeature = featureNameInput.value.trim() !== '';

    if ((hasFile || hasUrl) && hasFeature) {
        generateBtn.disabled = false;
    } else {
        generateBtn.disabled = true;
    }
}

let abortController = null;
const stopBtn = document.getElementById('stop-btn');

stopBtn.addEventListener('click', () => {
    if (abortController) {
        abortController.abort();
        abortController = null;

        // Update UI immediately
        stopBtn.classList.add('hidden');
        generateBtn.disabled = false;
        generateBtn.querySelector('.btn-text').textContent = 'Generate Test Cases';
        generateBtn.querySelector('.loader').classList.add('hidden');

        const statusMsg = document.getElementById('status-message');
        if (statusMsg) {
            statusMsg.textContent = 'Generation Stopped 🛑';
            setTimeout(() => {
                statusMsg.classList.add('hidden');
                statusMsg.textContent = '';
            }, 3000);
        }
    }
});

generateBtn.addEventListener('click', () => {
    const featureName = featureNameInput.value.trim();
    const testCaseLimit = document.getElementById('test-case-limit').value;
    const url = urlInput.value.trim();

    if ((!uploadedFilePath && !url) || !featureName) return;

    // UI Loading State
    generateBtn.disabled = true;
    generateBtn.querySelector('.btn-text').textContent = 'Generating...';
    generateBtn.querySelector('.loader').classList.remove('hidden');
    stopBtn.classList.remove('hidden'); // Show stop button
    resultsSection.classList.remove('hidden');
    testCasesContainer.innerHTML = '';
    hallucinationReport.classList.add('hidden');

    // Reset test cases array for new generation
    window.generatedTestCases = [];
    if (exportBtn) {
        exportBtn.classList.add('export-disabled');
    }

    // Initialize AbortController
    abortController = new AbortController();

    // Use fetch with ReadableStream for streaming
    fetch('http://127.0.0.1:8000/generate-stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
            file_path: uploadedFilePath || "",
            feature_name: featureName,
            test_case_limit: testCaseLimit ? parseInt(testCaseLimit) : null,
            url: url || null
        }),
        signal: abortController.signal
    })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            function processStream() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        console.log('Stream complete');
                        generateBtn.disabled = false;
                        generateBtn.querySelector('.btn-text').textContent = 'Generate Test Cases';
                        generateBtn.querySelector('.loader').classList.add('hidden');
                        stopBtn.classList.add('hidden'); // Hide stop button
                        return;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n\n');
                    buffer = lines.pop(); // Keep incomplete line in buffer

                    lines.forEach(line => {
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.substring(6));
                            handleStreamEvent(data);
                        }
                    });

                    processStream();
                }).catch(error => {
                    if (error.name === 'AbortError') {
                        console.log('Fetch aborted');
                    } else {
                        console.error('Stream error:', error);
                        displayError('An error occurred during generation.', 'stream_error');
                        generateBtn.disabled = false;
                        generateBtn.querySelector('.btn-text').textContent = 'Generate Test Cases';
                        generateBtn.querySelector('.loader').classList.add('hidden');
                        stopBtn.classList.add('hidden');
                    }
                });
            }

            processStream();
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('Fetch aborted');
            } else {
                console.error('Fetch error:', error);
                displayError('Failed to connect to server.', 'connection_error');
                generateBtn.disabled = false;
                generateBtn.querySelector('.btn-text').textContent = 'Generate Test Cases';
                generateBtn.querySelector('.loader').classList.add('hidden');
                stopBtn.classList.add('hidden');
            }
        });
});

function displayResults(data) {
    resultsSection.classList.remove('hidden');
    testCasesContainer.innerHTML = '';
    hallucinationList.innerHTML = '';

    const testCases = data.test_cases || [];
    const hallucinationInfo = data.hallucination_report || {};
    const isBatchMode = data.batch_mode || false;
    const featuresProcessed = data.features_processed || [];

    // Store test cases for export
    window.generatedTestCases = testCases;

    // Enable export button if we have test cases
    if (testCases.length > 0) {
        exportBtn.classList.remove('export-disabled');
    } else {
        exportBtn.classList.add('export-disabled');
    }

    // Display batch mode summary if applicable
    if (isBatchMode && featuresProcessed.length > 0) {
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'batch-summary';
        summaryDiv.innerHTML = `
            <h4>📊 Batch Processing Summary</h4>
            <p><strong>Features Processed:</strong> ${data.total_features}</p>
            <p><strong>Total Test Cases:</strong> ${data.total_test_cases}</p>
        `;
        testCasesContainer.appendChild(summaryDiv);
    }

    // Display Test Cases
    if (testCases.length === 0) {
        testCasesContainer.innerHTML += '<p>No test cases generated.</p>';
    } else {
        if (isBatchMode) {
            // Group test cases by feature
            const groupedByFeature = {};
            testCases.forEach(tc => {
                const featureName = tc.feature || 'Unknown Feature';
                if (!groupedByFeature[featureName]) {
                    groupedByFeature[featureName] = [];
                }
                groupedByFeature[featureName].push(tc);
            });

            // Display each feature group
            Object.keys(groupedByFeature).forEach(featureName => {
                const featureGroup = document.createElement('div');
                featureGroup.className = 'feature-group';

                const featureTestCases = groupedByFeature[featureName];
                const featureDesc = featureTestCases[0].feature_description || '';

                featureGroup.innerHTML = `
                    <h3>🎯 ${featureName}</h3>
                    ${featureDesc ? `<p>${featureDesc}</p>` : ''}
                `;

                featureTestCases.forEach(tc => {
                    const card = createTestCaseCard(tc);
                    featureGroup.appendChild(card);
                });

                testCasesContainer.appendChild(featureGroup);
            });
        } else {
            // Single feature mode - display normally
            testCases.forEach(tc => {
                const card = createTestCaseCard(tc);
                testCasesContainer.appendChild(card);
            });
        }
    }

    // Display Hallucination Report
    if (hallucinationInfo.found_issues) {
        hallucinationReport.classList.remove('hidden');
        hallucinationBadge.textContent = 'Potential Hallucinations Detected';
        hallucinationBadge.className = 'badge warning';

        hallucinationInfo.issues.forEach(issue => {
            const li = document.createElement('li');
            li.textContent = issue;
            hallucinationList.appendChild(li);
        });
    } else {
        hallucinationReport.classList.add('hidden');
        hallucinationBadge.textContent = 'Hallucination Check Passed';
        hallucinationBadge.className = 'badge success';
        hallucinationBadge.classList.remove('hidden');
    }
}

function createTestCaseCard(tc) {
    const card = document.createElement('div');
    card.className = 'test-case-card';

    // Handle both camelCase (Groq) and space-separated (Ollama) field names
    const testCaseId = tc['Test Case ID'] || tc['testCaseId'] || tc['testCaseID'] || tc['id'] || 'No ID';
    const description = tc['Description'] || tc['description'] || '';
    const preconditions = tc['Preconditions'] || tc['preconditions'] || '';
    const steps = tc['Steps'] || tc['steps'] || '';
    const expectedResult = tc['Expected Result'] || tc['expectedResult'] || '';

    let content = `<h4>${testCaseId}</h4>`;
    content += `<p><strong>Description:</strong> ${description}</p>`;
    content += `<p><strong>Preconditions:</strong> ${preconditions}</p>`;

    // Handle steps - could be array or string
    if (Array.isArray(steps)) {
        content += `<p><strong>Steps:</strong></p><ol>`;
        steps.forEach(step => {
            content += `<li>${step}</li>`;
        });
        content += `</ol>`;
    } else {
        content += `<p><strong>Steps:</strong> ${steps}</p>`;
    }

    content += `<p><strong>Expected Result:</strong> ${expectedResult}</p>`;

    if (tc.hallucination_flag) {
        content += `<p style="color: #f87171;"><strong>⚠️ Potential Hallucination:</strong> ${tc.hallucination_reason}</p>`;
    }

    card.innerHTML = content;
    return card;
}

function displayError(errorMessage, errorType) {
    resultsSection.classList.remove('hidden');
    testCasesContainer.innerHTML = '';

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';

    let icon = '❌';
    let title = 'Error';
    let suggestion = '';

    if (errorType === 'rate_limit') {
        icon = '⏱️';
        title = 'Rate Limit Exceeded';
        suggestion = '<p class="error-suggestion">💡 <strong>Suggestion:</strong> Switch to Ollama provider in the .env file or wait a few minutes for the rate limit to reset.</p>';
    } else if (errorType === 'network_error') {
        icon = '🌐';
        title = 'Network Error';
        suggestion = '<p class="error-suggestion">💡 <strong>Suggestion:</strong> Check if the backend server is running on port 8000.</p>';
    }

    errorDiv.innerHTML = `
        <div class="error-icon">${icon}</div>
        <h3>${title}</h3>
        <p class="error-text">${errorMessage}</p>
        ${suggestion}
    `;

    testCasesContainer.appendChild(errorDiv);
    hallucinationReport.classList.add('hidden');
    hallucinationBadge.classList.add('hidden');
}

// Stream event handler
let streamedTestCases = [];
let currentBatchMode = false;

function handleStreamEvent(event) {
    console.log('Stream event:', event);

    switch (event.type) {
        case 'status':
            console.log('Status:', event.message);
            const statusMsg = document.getElementById('status-message');
            if (statusMsg) {
                statusMsg.textContent = event.message;
                statusMsg.classList.remove('hidden');
            }
            break;

        case 'batch_start':
            currentBatchMode = true;
            streamedTestCases = [];

            // Show batch summary with progress
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'batch-summary';
            summaryDiv.id = 'streaming-summary';
            summaryDiv.innerHTML = `
                <h4>📊 Batch Processing</h4>
                <p><strong>Total Features:</strong> ${event.total_features}</p>
                <p id="progress-text"><strong>Progress:</strong> 0/${event.total_features} features processed</p>
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progress-bar"></div>
                </div>
            `;
            testCasesContainer.appendChild(summaryDiv);
            break;

        case 'progress':
            // Update progress
            const percentage = (event.current / event.total) * 100;
            const progressText = document.getElementById('progress-text');
            const progressBar = document.getElementById('progress-bar');

            if (progressText) {
                progressText.innerHTML = `<strong>Progress:</strong> ${event.current}/${event.total} features - Current: ${event.feature}`;
            }
            if (progressBar) {
                progressBar.style.width = `${percentage}%`;
            }
            break;

        case 'test_case':
            // Add test case progressively
            const tc = event.test_case;
            const feature = event.feature || 'Test Cases';  // Default for single feature mode

            // Find or create feature group
            let featureGroup = null;
            if (currentBatchMode && feature) {
                const featureId = `feature-${feature.replace(/\s+/g, '-')}`;
                featureGroup = document.getElementById(featureId);

                if (!featureGroup) {
                    featureGroup = document.createElement('div');
                    featureGroup.className = 'feature-group';
                    featureGroup.id = featureId;
                    featureGroup.innerHTML = `
                        <h3>🎯 ${feature}</h3>
                        ${tc.feature_description ? `<p>${tc.feature_description}</p>` : ''}
                    `;
                    testCasesContainer.appendChild(featureGroup);
                }
            }

            // Create and add test case card
            const card = createTestCaseCard(tc);
            if (featureGroup) {
                featureGroup.appendChild(card);
            } else {
                testCasesContainer.appendChild(card);
            }

            // Store test case for export
            if (!window.generatedTestCases) {
                window.generatedTestCases = [];
            }
            window.generatedTestCases.push(tc);

            // Enable export button
            if (exportBtn) {
                exportBtn.classList.remove('export-disabled');
            }
            break;

        case 'complete':
            // Final completion
            const result = event.result;

            // Update hallucination report
            const hallucinationInfo = result.hallucination_report || {};
            if (hallucinationInfo.found_issues) {
                hallucinationReport.classList.remove('hidden');
                hallucinationBadge.textContent = 'Potential Hallucinations Detected';
                hallucinationBadge.className = 'badge warning';

                hallucinationList.innerHTML = '';
                hallucinationInfo.issues.forEach(issue => {
                    const li = document.createElement('li');
                    li.textContent = issue;
                    hallucinationList.appendChild(li);
                });
            } else {
                hallucinationBadge.textContent = 'Hallucination Check Passed';
                hallucinationBadge.className = 'badge success';
                hallucinationBadge.classList.remove('hidden');
            }

            currentBatchMode = false;

            // Clear status message
            const completionStatusMsg = document.getElementById('status-message');
            if (completionStatusMsg) {
                completionStatusMsg.textContent = 'Generation Complete ✅';
                setTimeout(() => {
                    completionStatusMsg.classList.add('hidden');
                    completionStatusMsg.textContent = '';
                }, 3000);
            }
            break;

        case 'error':
            displayError(event.message, 'generation_error');
            break;
    }
}
