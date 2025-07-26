document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pdfForm');
    const fileInput = document.getElementById('files');
    const operationSelect = document.getElementById('operation');
    const submitBtn = document.getElementById('submitBtn');
    const resultDiv = document.getElementById('result');
    const progressDiv = document.getElementById('progress');
    
    let hasProcessedFile = false;

    // Form submit handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const operation = operationSelect.value;
        
        if (!operation) {
            showError('ಕಾರ್ಯಾಚರಣೆ ಆಯ್ಕೆ ಮಾಡಿ');
            return;
        }

        // Check if using previous file or new upload
        if (hasProcessedFile && !fileInput.files.length) {
            formData.append('use_previous', 'true');
        } else if (!fileInput.files.length) {
            showError('ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ');
            return;
        }

        processOperation(formData);
    });

    function processOperation(formData) {
        showProgress();
        submitBtn.disabled = true;

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideProgress();
            submitBtn.disabled = false;

            if (data.success) {
                showSuccess(data);
                if (data.can_chain) {
                    hasProcessedFile = true;
                    showChainOptions();
                }
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            hideProgress();
            submitBtn.disabled = false;
            showError('ಸರ್ವರ್ ದೋಷ');
        });
    }

    function showSuccess(data) {
        resultDiv.innerHTML = `
            <div class="success-message">
                <h3>✓ ${data.message}</h3>
                <div class="download-section">
                    <a href="${data.download_url}" class="download-btn" download>
                        📥 ${data.filename} ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ
                    </a>
                </div>
            </div>
        `;
        resultDiv.style.display = 'block';
    }

    function showChainOptions() {
        const chainDiv = document.createElement('div');
        chainDiv.className = 'chain-options';
        chainDiv.innerHTML = `
            <div class="chain-message">
                <h4>🔗 ಮತ್ತೊಂದು ಕಾರ್ಯಾಚರಣೆ ಮಾಡಿ</h4>
                <p>ಪ್ರಕ್ರಿಯೆಗೊಂಡ ಫೈಲ್‌ನೊಂದಿಗೆ ಮತ್ತೊಂದು ಕಾರ್ಯಾಚರಣೆ ಮಾಡಬಹುದು</p>
                <button type="button" class="reset-btn" onclick="resetSession()">
                    🔄 ಹೊಸ ಫೈಲ್‌ಗಳೊಂದಿಗೆ ಪ್ರಾರಂಭಿಸಿ
                </button>
            </div>
        `;
        resultDiv.appendChild(chainDiv);
        
        // Update file input label
        updateFileInputLabel();
    }

    function updateFileInputLabel() {
        const fileLabel = document.querySelector('label[for="files"]');
        if (fileLabel && hasProcessedFile) {
            fileLabel.innerHTML = '📎 ಹೊಸ ಫೈಲ್‌ಗಳು (ಐಚ್ಛಿಕ - ಪ್ರಕ್ರಿಯೆಗೊಂಡ ಫೈಲ್ ಬಳಸಲಾಗುವುದು)';
            fileInput.required = false;
        }
    }

    function resetSession() {
        fetch('/reset', { method: 'POST' })
        .then(() => {
            hasProcessedFile = false;
            resultDiv.style.display = 'none';
            form.reset();
            fileInput.required = true;
            document.querySelector('label[for="files"]').innerHTML = '📎 ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ';
        });
    }

    function showError(message) {
        resultDiv.innerHTML = `
            <div class="error-message">
                <h3>❌ ದೋಷ</h3>
                <p>${message}</p>
            </div>
        `;
        resultDiv.style.display = 'block';
    }

    function showProgress() {
        progressDiv.style.display = 'block';
        resultDiv.style.display = 'none';
    }

    function hideProgress() {
        progressDiv.style.display = 'none';
    }

    // Operation change handler for dynamic form fields
    operationSelect.addEventListener('change', function() {
        const pagesField = document.getElementById('pagesField');
        const compressionField = document.getElementById('compressionField');
        
        // Hide all optional fields
        if (pagesField) pagesField.style.display = 'none';
        if (compressionField) compressionField.style.display = 'none';
        
        // Show relevant fields based on operation
        const operation = this.value;
        if (['split', 'extract', 'delete'].includes(operation) && pagesField) {
            pagesField.style.display = 'block';
        }
        if (operation === 'compress' && compressionField) {
            compressionField.style.display = 'block';
        }
    });

    // Make resetSession globally available
    window.resetSession = resetSession;
});