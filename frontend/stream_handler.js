
// Stream event handler
let streamedTestCases = [];
let streamedFeatures = [];
let currentBatchMode = false;
let totalFeatures = 0;

function handleStreamEvent(event) {
    console.log('Stream event:', event);

    switch (event.type) {
        case 'status':
            console.log('Status:', event.message);
            break;

        case 'batch_start':
            currentBatchMode = true;
            totalFeatures = event.total_features;
            streamedTestCases = [];
            streamedFeatures = [];

            // Show batch summary
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'batch-summary';
            summaryDiv.id = 'streaming-summary';
            summaryDiv.innerHTML = `
                <h4>📊 Batch Processing</h4>
                <p><strong>Total Features:</strong> ${totalFeatures}</p>
                <p id="progress-text"><strong>Progress:</strong> 0/${totalFeatures} features processed</p>
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
                </div>
            `;
            testCasesContainer.appendChild(summaryDiv);
            break;

        case 'progress':
            // Update progress
            const current = event.current;
            const total = event.total;
            const feature = event.feature;
            const percentage = (current / total) * 100;

            const progressText = document.getElementById('progress-text');
            const progressBar = document.getElementById('progress-bar');

            if (progressText) {
                progressText.innerHTML = `<strong>Progress:</strong> ${current}/${total} features processed - Current: ${feature}`;
            }
            if (progressBar) {
                progressBar.style.width = `${percentage}%`;
            }
            break;

        case 'test_case':
            // Add test case progressively
            const tc = event.test_case;
            const feature = event.feature;

            streamedTestCases.push(tc);

            // Find or create feature group
            let featureGroup = document.getElementById(`feature-${feature.replace(/\s+/g, '-')}`);
            if (!featureGroup && currentBatchMode) {
                featureGroup = document.createElement('div');
                featureGroup.className = 'feature-group';
                featureGroup.id = `feature-${feature.replace(/\s+/g, '-')}`;
                featureGroup.innerHTML = `
                    <h3>🎯 ${feature}</h3>
                    ${tc.feature_description ? `<p>${tc.feature_description}</p>` : ''}
                `;
                testCasesContainer.appendChild(featureGroup);
            }

            // Create and add test case card
            const card = createTestCaseCard(tc);
            if (featureGroup) {
                featureGroup.appendChild(card);
            } else {
                testCasesContainer.appendChild(card);
            }
            break;

        case 'complete':
            // Final completion
            console.log('Generation complete');
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

            // Reset state
            currentBatchMode = false;
            streamedTestCases = [];
            streamedFeatures = [];
            break;

        case 'error':
            displayError(event.message, 'generation_error');
            break;
    }
}
