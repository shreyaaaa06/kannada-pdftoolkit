class KannadaPDFToolkit {
    constructor() {
        this.selectedFiles = [];
        this.currentOperation = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // Operation buttons
        document.querySelectorAll('.operation-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectOperation(btn.dataset.operation);
            });
        });

        // File input
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e.target.files);
            });
        }

        // Process button
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.addEventListener('click', () => {
                this.processFiles();
            });
        }

        // Modal close
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                this.closeModal();
            });
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFileSelection(e.dataTransfer.files);
        });

        uploadArea.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
    }

    selectOperation(operation) {
        this.currentOperation = operation;
        this.clearFiles();
        this.showUploadModal(operation);
    }

    handleFileSelection(files) {
        this.selectedFiles = Array.from(files);
        this.displaySelectedFiles();
        this.updateProcessButton();
    }

    displaySelectedFiles() {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;

        if (this.selectedFiles.length === 0) {
            fileList.style.display = 'none';
            return;
        }

        fileList.style.display = 'block';
        fileList.innerHTML = this.selectedFiles.map((file, index) => `
            <div class="file-item">
                <span class="file-icon">📄</span>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
                <span class="file-remove" onclick="kannadaPDF.removeFile(${index})">×</span>
            </div>
        `).join('');
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.displaySelectedFiles();
        this.updateProcessButton();
    }

    clearFiles() {
        this.selectedFiles = [];
        this.displaySelectedFiles();
        this.updateProcessButton();
    }

    updateProcessButton() {
        const processBtn = document.getElementById('processBtn');
        if (!processBtn) return;

        processBtn.disabled = this.selectedFiles.length === 0;
        processBtn.textContent = this.selectedFiles.length > 0 ? 
            'ಪ್ರಕ್ರಿಯೆ ಮಾಡಿ' : 'ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ';
    }

    async processFiles() {
        if (this.selectedFiles.length === 0) {
            this.showAlert('ದಯವಿಟ್ಟು ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ', 'error');
            return;
        }

        this.showProcessingModal();
        
        try {
            const formData = new FormData();
            formData.append('operation', this.currentOperation);

            // Add files
            this.selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            // Add operation parameters
            const pages = document.getElementById('pagesInput');
            if (pages && pages.value) {
                formData.append('pages', pages.value);
            }

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccessModal(result);
            } else {
                throw new Error(result.error || 'ಅಜ್ಞಾತ ದೋಷ');
            }

        } catch (error) {
            console.error('Processing error:', error);
            this.showErrorModal(error.message);
        }
    }

    showUploadModal(operation) {
        const modal = document.getElementById('uploadModal');
        const title = document.getElementById('modalTitle');
        const content = document.getElementById('modalContent');

        if (!modal) return;

        title.textContent = this.getOperationTitle(operation);
        content.innerHTML = this.getOperationForm(operation);

        modal.style.display = 'block';
        
        // Re-setup event listeners
        this.setupUploadArea();
        this.setupFormListeners();
    }

    setupUploadArea() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e.target.files);
            });

            this.setupDragAndDrop();
        }
    }

    setupFormListeners() {
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.addEventListener('click', () => {
                this.processFiles();
            });
        }
    }

    getOperationTitle(operation) {
        const titles = {
            'merge': 'PDF ಗಳನ್ನು ವಿಲೀನಗೊಳಿಸಿ',
            'split': 'PDF ಅನ್ನು ವಿಭಾಗಿಸಿ',
            'extract': 'ಪುಟಗಳನ್ನು ಹೊರತೆಗೆಯಿರಿ',
            'compress': 'PDF ಸಂಕುಚಿಸಿ',
            'pdf_to_jpeg': 'PDF ನಿಂದ JPEG ಗೆ',
            'jpeg_to_pdf': 'JPEG ನಿಂದ PDF ಗೆ'
        };
        return titles[operation] || operation;
    }

    getOperationForm(operation) {
        let form = `
            <div id="uploadArea" class="upload-area">
                <span class="upload-icon">📁</span>
                <div class="upload-text">ಫೈಲ್‌ಗಳನ್ನು ಇಲ್ಲಿ ಎಳೆಯಿರಿ</div>
                <div class="upload-subtext">ಅಥವಾ ಕ್ಲಿಕ್ ಮಾಡಿ</div>
                <input type="file" id="fileInput" style="display: none;" multiple>
            </div>
            <div id="fileList" class="file-list" style="display: none;"></div>
        `;

        // Add page input for operations that need it
        if (['split', 'extract'].includes(operation)) {
            form += `
                <div class="form-group">
                    <label class="form-label">ಪುಟ ಸಂಖ್ಯೆಗಳು:</label>
                    <input type="text" id="pagesInput" class="form-input" 
                           placeholder="ಉದಾ: 1-3,5,7-9">
                    <small class="form-help">ಉದಾ: 1-3,5,7-9</small>
                </div>
            `;
        }

        form += `
            <div style="margin-top: 2rem;">
                <button id="processBtn" class="btn btn-primary" disabled>
                    ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ
                </button>
            </div>
        `;

        return form;
    }

    showProcessingModal() {
        const modal = document.getElementById('uploadModal');
        const content = document.getElementById('modalContent');

        content.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <div class="spinner" style="width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #D4AF37; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 2rem;"></div>
                <h3>ಪ್ರಕ್ರಿಯೆ ನಡೆಯುತ್ತಿದೆ...</h3>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
    }

    showSuccessModal(result) {
        const modal = document.getElementById('uploadModal');
        const content = document.getElementById('modalContent');

        content.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; color: #28a745; margin-bottom: 1rem;">✅</div>
                <h3>ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!</h3>
                <p style="margin: 1rem 0;">${result.message}</p>
                <div style="margin-top: 2rem;">
                    <a href="${result.download_url}" class="btn btn-primary" 
                       download="${result.filename}" style="margin-right: 1rem;">
                        📥 ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ
                    </a>
                    <button class="btn" onclick="kannadaPDF.closeModal()">
                        ಮುಚ್ಚಿ
                    </button>
                </div>
            </div>
        `;

        // Auto-download after 2 seconds
        setTimeout(() => {
            const link = document.createElement('a');
            link.href = result.download_url;
            link.download = result.filename;
            link.click();
        }, 2000);
    }

    showErrorModal(errorMessage) {
        const modal = document.getElementById('uploadModal');
        const content = document.getElementById('modalContent');

        content.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; color: #dc3545; margin-bottom: 1rem;">❌</div>
                <h3>ದೋಷ ಸಂಭವಿಸಿದೆ</h3>
                <p style="margin: 1rem 0;">${errorMessage}</p>
                <div style="margin-top: 2rem;">
                    <button class="btn btn-primary" onclick="kannadaPDF.retryOperation()">
                        ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ
                    </button>
                    <button class="btn" onclick="kannadaPDF.closeModal()">
                        ಮುಚ್ಚಿ
                    </button>
                </div>
            </div>
        `;
    }

    retryOperation() {
        if (this.currentOperation) {
            this.showUploadModal(this.currentOperation);
        }
    }

    closeModal() {
        const modal = document.getElementById('uploadModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `<span>${message}</span>`;
        alert.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 1000;
            padding: 1rem; border-radius: 5px; color: white;
            background: ${type === 'error' ? '#dc3545' : '#28a745'};
        `;

        document.body.appendChild(alert);
        setTimeout(() => alert.remove(), 3000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.kannadaPDF = new KannadaPDFToolkit();
    
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('uploadModal');
        if (e.target === modal) {
            window.kannadaPDF.closeModal();
        }
    });
});

// Operation selection function for buttons
function selectOperation(operation) {
    if (window.kannadaPDF) {
        window.kannadaPDF.selectOperation(operation);
    }
}