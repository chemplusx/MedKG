function exportResults() {
    const format = prompt('Choose export format (csv/json):', 'csv');
    if (!format) return;

    showLoading();

    // Simulate export process
    setTimeout(() => {
        const filename = `medkg_export_${new Date().toISOString().split('T')[0]}.${format}`;
        // In real implementation, this would create and download actual file
        console.log(`Exporting results as ${filename}`);
        hideLoading();
        showNotification('Export completed successfully');
    }, 1000);
}

function exportEntry(id) {
    showLoading();

    // Open a modal to let user choose export format
    const formatChoices = ['JSON', 'CSV', 'BibTeX'];
    const modalHTML = `
<div id="exportModal" class="modal">
    <div class="modal-content">
        <h4>Export Entry</h4>
        <p>Choose export format:</p>
        <div class="input-field-1">
            <select id="exportFormat">
                ${formatChoices.map(format =>
        `<option value="${format.toLowerCase()}">${format}</option>`
    ).join('')}
            </select>
        </div>
    </div>
    <div class="modal-footer">
        <button class="modal-close btn-flat">Cancel</button>
        <button class="btn waves-effect waves-light" onclick="proceedWithExport('${id}')">
            Export
        </button>
    </div>
</div>
`;

    // Add modal to document if it doesn't exist
    if (!document.getElementById('exportModal')) {
        const modalElement = document.createElement('div');
        modalElement.innerHTML = modalHTML;
        document.body.appendChild(modalElement.firstElementChild);
    }

    // Initialize and open modal
    const modal = document.getElementById('exportModal');
    const instance = M.Modal.init(modal);

    // Initialize select
    const select = modal.querySelector('select');
    M.FormSelect.init(select);

    instance.open();
    hideLoading();
}

function proceedWithExport(id) {
    showLoading();

    const format = document.getElementById('exportFormat').value;

    // In a real implementation, this would fetch the data from your backend
    fetch(`api/node-details?id=${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch entry data');
            }
            return response.json();
        })
        .then(data => {
            let exportData;
            let mimeType;
            let fileExtension;

            switch (format) {
                case 'json':
                    exportData = JSON.stringify(data, null, 2);
                    mimeType = 'application/json';
                    fileExtension = 'json';
                    break;

                case 'csv':
                    // Convert data to CSV format
                    const csvRows = [];
                    // Add headers
                    csvRows.push(Object.keys(data).join(','));
                    // Add values
                    csvRows.push(Object.values(data).map(value =>
                        typeof value === 'string' ? `"${value}"` : value
                    ).join(','));
                    exportData = csvRows.join('\n');
                    mimeType = 'text/csv';
                    fileExtension = 'csv';
                    break;

                case 'bibtex':
                    // Format as BibTeX
                    exportData = `@article{medkg_${id},
                        title = {${data.name || 'Untitled'}},
                        author = {MedKG Database},
                        year = {${new Date().getFullYear()}},
                        journal = {MedKG Knowledge Graph},
                        note = {Entry ID: ${id}}
                    }`;
                    mimeType = 'text/plain';
                    fileExtension = 'bib';
                    break;

                default:
                    throw new Error('Unsupported export format');
            }

            // Create and trigger download
            const blob = new Blob([exportData], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `medkg_entry_${id}_${new Date().toISOString().split('T')[0]}.${fileExtension}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            hideLoading();
            showNotification(`Entry exported successfully as ${format.toUpperCase()}`);
        })
        .catch(error => {
            console.error('Export error:', error);
            hideLoading();
            showError('Failed to export entry. Please try again.');
        })
        .finally(() => {
            // Close the modal
            const modalInstance = M.Modal.getInstance(document.getElementById('exportModal'));
            if (modalInstance) {
                modalInstance.close();
            }
        });
}