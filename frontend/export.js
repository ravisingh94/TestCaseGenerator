console.log('🔧 export.js file is loading...');

// Export functionality - runs immediately since script is loaded at end of body
(function () {
    const exportBtn = document.getElementById('export-btn');
    const exportMenu = document.getElementById('export-menu');

    console.log('Export script loaded', { exportBtn, exportMenu });
    console.log('Export button disabled?', exportBtn.disabled);
    console.log('Export button classes:', exportBtn.className);

    if (!exportBtn || !exportMenu) {
        console.error('Export button or menu not found');
        return;
    }

    // Try multiple ways to attach the event
    // Method 1: addEventListener
    exportBtn.addEventListener('click', (e) => {
        console.log('Export button clicked (addEventListener)');
        e.preventDefault();
        e.stopPropagation();
        exportMenu.classList.toggle('hidden');
    }, true); // Use capture phase

    // Method 2: onclick property as backup
    exportBtn.onclick = function (e) {
        // Don't do anything if button is disabled
        if (exportBtn.classList.contains('export-disabled')) {
            console.log('Export button is disabled, ignoring click');
            return;
        }

        console.log('Export button clicked (onclick)');
        e.preventDefault();
        e.stopPropagation();
        exportMenu.classList.toggle('hidden');
    };

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!exportBtn.contains(e.target) && !exportMenu.contains(e.target)) {
            exportMenu.classList.add('hidden');
        }
    });

    // Export option handlers
    document.querySelectorAll('.export-option').forEach(option => {
        option.addEventListener('click', () => {
            console.log('Export option clicked:', option.dataset.format);
            const format = option.dataset.format;
            exportMenu.classList.add('hidden');

            // Access generatedTestCases from window scope
            const testCases = window.generatedTestCases || [];
            console.log('Test cases to export:', testCases.length);

            switch (format) {
                case 'txt':
                    exportAsTXT();
                    break;
                case 'json':
                    exportAsJSON();
                    break;
                case 'docx':
                    exportAsDOCX();
                    break;
                case 'pdf':
                    exportAsPDF();
                    break;
            }
        });
    });
})();

// Export Functions
function exportAsTXT() {
    let content = 'TEST CASES\n';
    content += '='.repeat(80) + '\n\n';

    window.generatedTestCases.forEach((tc, index) => {
        const testCaseId = tc['Test Case ID'] || tc['testCaseId'] || tc['testCaseID'] || tc['id'] || `TC-${index + 1}`;
        const description = tc['Description'] || tc['description'] || '';
        const preconditions = tc['Preconditions'] || tc['preconditions'] || '';
        const steps = tc['Steps'] || tc['steps'] || '';
        const expectedResult = tc['Expected Result'] || tc['expectedResult'] || '';

        content += `${testCaseId}\n`;
        content += '-'.repeat(80) + '\n';
        content += `Description: ${description}\n`;
        content += `Preconditions: ${preconditions}\n`;
        content += `Steps: ${Array.isArray(steps) ? steps.join(', ') : steps}\n`;
        content += `Expected Result: ${expectedResult}\n\n`;
    });

    downloadFile(content, 'test-cases.txt', 'text/plain');
}

function exportAsJSON() {
    const content = JSON.stringify(window.generatedTestCases, null, 2);
    downloadFile(content, 'test-cases.json', 'application/json');
}

function exportAsDOCX() {
    try {
        const { Document, Packer, Paragraph, TextRun, HeadingLevel } = docx;

        const children = [
            new Paragraph({
                text: 'Test Cases',
                heading: HeadingLevel.HEADING_1,
            }),
        ];

        window.generatedTestCases.forEach((tc, index) => {
            const testCaseId = tc['Test Case ID'] || tc['testCaseId'] || tc['testCaseID'] || tc['id'] || `TC-${index + 1}`;
            const description = tc['Description'] || tc['description'] || '';
            const preconditions = tc['Preconditions'] || tc['preconditions'] || '';
            const steps = tc['Steps'] || tc['steps'] || '';
            const expectedResult = tc['Expected Result'] || tc['expectedResult'] || '';

            children.push(
                new Paragraph({
                    text: testCaseId,
                    heading: HeadingLevel.HEADING_2,
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: 'Description: ', bold: true }),
                        new TextRun(description),
                    ],
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: 'Preconditions: ', bold: true }),
                        new TextRun(preconditions),
                    ],
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: 'Steps: ', bold: true }),
                        new TextRun(Array.isArray(steps) ? steps.join(', ') : steps),
                    ],
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: 'Expected Result: ', bold: true }),
                        new TextRun(expectedResult),
                    ],
                }),
                new Paragraph({ text: '' }) // Empty line
            );
        });

        const doc = new Document({
            sections: [{
                children: children,
            }],
        });

        Packer.toBlob(doc).then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'test-cases.docx';
            a.click();
            URL.revokeObjectURL(url);
        });
    } catch (error) {
        console.error('DOCX export error:', error);
        alert('Error exporting to DOCX. Please try another format.');
    }
}

function exportAsPDF() {
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        let yPosition = 20;
        const pageHeight = doc.internal.pageSize.height;
        const margin = 20;
        const lineHeight = 7;

        // Title
        doc.setFontSize(18);
        doc.setFont(undefined, 'bold');
        doc.text('Test Cases', margin, yPosition);
        yPosition += 15;

        window.generatedTestCases.forEach((tc, index) => {
            // Convert all values to strings to avoid jsPDF errors
            const testCaseId = String(tc['Test Case ID'] || tc['testCaseId'] || tc['testCaseID'] || tc['id'] || `TC-${index + 1}`);
            const description = String(tc['Description'] || tc['description'] || '');
            const preconditions = String(tc['Preconditions'] || tc['preconditions'] || '');
            const steps = Array.isArray(tc['Steps'] || tc['steps'])
                ? (tc['Steps'] || tc['steps']).join(', ')
                : String(tc['Steps'] || tc['steps'] || '');
            const expectedResult = String(tc['Expected Result'] || tc['expectedResult'] || '');

            // Check if we need a new page
            if (yPosition > pageHeight - 40) {
                doc.addPage();
                yPosition = 20;
            }

            // Test Case ID
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.text(testCaseId, margin, yPosition);
            yPosition += lineHeight + 2;

            // Description
            doc.setFontSize(11);
            doc.setFont(undefined, 'bold');
            doc.text('Description:', margin, yPosition);
            doc.setFont(undefined, 'normal');
            const descLines = doc.splitTextToSize(description, 170);
            doc.text(descLines, margin + 30, yPosition);
            yPosition += descLines.length * lineHeight;

            // Preconditions
            doc.setFont(undefined, 'bold');
            doc.text('Preconditions:', margin, yPosition);
            doc.setFont(undefined, 'normal');
            const preLines = doc.splitTextToSize(preconditions, 170);
            doc.text(preLines, margin + 30, yPosition);
            yPosition += preLines.length * lineHeight;

            // Steps
            doc.setFont(undefined, 'bold');
            doc.text('Steps:', margin, yPosition);
            doc.setFont(undefined, 'normal');
            const stepLines = doc.splitTextToSize(steps, 170);
            doc.text(stepLines, margin + 30, yPosition);
            yPosition += stepLines.length * lineHeight;

            // Expected Result
            doc.setFont(undefined, 'bold');
            doc.text('Expected Result:', margin, yPosition);
            doc.setFont(undefined, 'normal');
            const expLines = doc.splitTextToSize(expectedResult, 170);
            doc.text(expLines, margin + 30, yPosition);
            yPosition += expLines.length * lineHeight + 10;
        });

        doc.save('test-cases.pdf');
    } catch (error) {
        console.error('PDF export error:', error);
        alert('Error exporting to PDF. Please try another format.');
    }
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
