
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
