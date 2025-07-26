// Kannada PDF Toolkit - Frontend JavaScript

class KannadaPDFToolkit {
    constructor() {
        this.selectedFiles = [];
        this.currentOperation = null;
        this.sessionId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.generateSessionId();
        this.loadKannadaMessages();
    }

    generateSessionId() {
        this.sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    loadKannadaMessages() {
        this.messages = {
            selectOperation: 'ಕಾರ್ಯಾಚರಣೆ ಆಯ್ಕೆ ಮಾಡಿ',
            selectFiles: 'ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ',
            processing: 'ಪ್ರಕ್ರಿಯೆ ನಡೆಯುತ್ತಿದೆ...',
            completed: 'ಪೂರ್ಣಗೊಂಡಿದೆ!',
            error: 'ದೋಷ ಸಂಭವಿಸಿದೆ',
            invalidFile: 'ಅಮಾನ್ಯ ಫೈಲ್ ಪ್ರಕಾರ',
            noFiles: 'ದಯವಿಟ್ಟು ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ',
            dragFiles: 'ಫೈಲ್‌ಗಳನ್ನು ಇಲ್ಲಿ ಎಳೆಯಿರಿ',
            clickToSelect: 'ಅಥವಾ ಆಯ್ಕೆ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ',
            downloadReady: 'ಡೌನ್‌ಲೋಡ್ ತಯಾರಾಗಿದೆ',
            startProcess: 'ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ',
            clear: 'ಸ್ಪಷ್ಟಗೊಳಿಸಿ',
            download: 'ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ',
            close: 'ಮುಚ್ಚಿ',
            retry: 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ',
            fileTooLarge: 'ಫೈಲ್ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ',
            networkError: 'ನೆಟ್‌ವರ್ಕ್ ದೋಷ',
            serverError: 'ಸರ್ವರ್ ದೋಷ'
        };
    }

    setupEventListeners() {
        // Operation selection
        document.querySelectorAll('.operation-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectOperation(btn.dataset.operation);
            });
        });

        // File input change
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
        document.querySelectorAll('.close, .modal-close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                this.closeModal();
            });
        });

        // Clear files button
        const clearBtn = document.getElementById('clearFiles');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearFiles();
            });
        }

        // Close modal on outside click
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('uploadModal');
            if (e.target === modal) {
                this.closeModal();
            }
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
        this.updateFileInputAccept(operation);
    }

    updateFileInputAccept(operation) {
        const fileInput = document.getElementById('fileInput');
        const acceptMap = {
            'merge': '.pdf',
            'split': '.pdf',
            'extract': '.pdf',
            'delete': '.pdf',
            'crop': '.pdf',
            'rotate': '.pdf',
            'compress': '.pdf',
            'pdf_to_word': '.pdf',
            'word_to_pdf': '.doc,.docx',
            'pdf_to_jpeg': '.pdf',
            'jpeg_to_pdf': '.jpg,.jpeg,.png,.bmp,.tiff'
        };
        
        fileInput.accept = acceptMap[operation] || '*';
    }

    handleFileSelection(files) {
        const validFiles = this.validateFiles(files);
        
        if (validFiles.length === 0) {
            this.showAlert(this.messages.invalidFile, 'error');
            return;
        }

        this.selectedFiles = validFiles;
        this.displaySelectedFiles();
        this.updateProcessButton();
    }

    validateFiles(files) {
        const validFiles = [];
        const allowedTypes = this.getAllowedTypes(this.currentOperation);
        const maxFileSize = 10 * 1024 * 1024; // 10MB limit

        for (let file of files) {
            if (file.size > maxFileSize) {
                this.showAlert(`${file.name}: ${this.messages.fileTooLarge}`, 'error');
                continue;
            }

            const fileType = file.type;
            const fileName = file.name.toLowerCase();
            const fileExtension = fileName.substring(fileName.lastIndexOf('.'));

            if (this.isValidFileType(fileType, fileExtension, allowedTypes)) {
                validFiles.push(file);
            }
        }

        return validFiles;
    }

    getAllowedTypes(operation) {
        const typeMap = {
            'merge': ['application/pdf'],
            'split': ['application/pdf'],
            'extract': ['application/pdf'],
            'delete': ['application/pdf'],
            'crop': ['application/pdf'],
            'rotate': ['application/pdf'],
            'compress': ['application/pdf'],
            'pdf_to_word': ['application/pdf'],
            'word_to_pdf': ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            'pdf_to_jpeg': ['application/pdf'],
            'jpeg_to_pdf': ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff']
        };

        return typeMap[operation] || [];
    }

    isValidFileType(mimeType, extension, allowedTypes) {
        // Check MIME type
        if (allowedTypes.includes(mimeType)) {
            return true;
        }

        // Check extension as fallback
        const extensionMap = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        };

        return allowedTypes.includes(extensionMap[extension]);
    }

    displaySelectedFiles() {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;

        fileList.innerHTML = '';

        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item fade-in';
            fileItem.innerHTML = `
                <span class="file-icon">📄</span>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
                <span class="file-remove" onclick="kannadaPDF.removeFile(${index})">×</span>
            `;
            fileList.appendChild(fileItem);
        });
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

        if (this.selectedFiles.length > 0 && this.currentOperation) {
            processBtn.disabled = false;
            processBtn.textContent = this.messages.startProcess;
        } else {
            processBtn.disabled = true;
            processBtn.textContent = this.messages.selectFiles;
        }
    }

    async processFiles() {
        if (this.selectedFiles.length === 0) {
            this.showAlert(this.messages.noFiles, 'error');
            return;
        }

        this.showProcessingModal();
        
        try {
            const formData = new FormData();
            formData.append('operation', this.currentOperation);
            formData.append('session_id', this.sessionId);

            // Add files
            this.selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            // Add operation-specific parameters
            this.addOperationParameters(formData);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                this.showSuccessModal(result);
            } else {
                throw new Error(result.error || 'Unknown error');
            }

        } catch (error) {
            console.error('Processing error:', error);
            this.showErrorModal(error.message);
        }
    }

    addOperationParameters(formData) {
        // Add parameters based on current operation
        const params = this.getOperationParameters();
        
        for (const [key, value] of Object.entries(params)) {
            formData.append(key, value);
        }
    }

    getOperationParameters() {
        const params = {};

        // Get parameters from form inputs
        const pagesInput = document.getElementById('pages');
        if (pagesInput && pagesInput.value) {
            params.pages = pagesInput.value;
        }

        const angleSelect = document.getElementById('angle');
        if (angleSelect && angleSelect.value) {
            params.angle = angleSelect.value;
        }

        const qualitySelect = document.getElementById('quality');
        if (qualitySelect && qualitySelect.value) {
            params.quality = qualitySelect.value;
        }

        // Crop parameters
        ['left', 'top', 'right', 'bottom'].forEach(side => {
            const input = document.getElementById(side);
            if (input && input.value) {
                params[side] = parseFloat(input.value) || 0;
            }
        });

        return params;
    }

    showUploadModal(operation) {
        const modal = document.getElementById('uploadModal');
        const title = document.getElementById('modalTitle');
        const content = document.getElementById('modalContent');

        if (!modal) return;

        title.textContent = this.getOperationTitle(operation);
        content.innerHTML = this.getOperationForm(operation);

        modal.style.display = 'block';
        modal.classList.add('fade-in');

        // Re-setup event listeners for new elements
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

            // Re-setup drag and drop for the new upload area
            this.setupDragAndDrop();
        }
    }

    setupFormListeners() {
        const processBtn = document.getElementById('processBtn');
        const clearBtn = document.getElementById('clearFiles');

        if (processBtn) {
            processBtn.addEventListener('click', () => {
                this.processFiles();
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearFiles();
            });
        }
    }

    getOperationTitle(operation) {
        const titles = {
            'merge': 'PDF ಗಳನ್ನು ವಿಲೀನಗೊಳಿಸಿ',
            'split': 'PDF ಅನ್ನು ವಿಭಾಗಿಸಿ',
            'extract': 'ಪುಟಗಳನ್ನು ಹೊರತೆಗೆಯಿರಿ',
            'delete': 'ಪುಟಗಳನ್ನು ಅಳಿಸಿ',
            'crop': 'ಪುಟಗಳನ್ನು ಕತ್ತರಿಸಿ',
            'rotate': 'ಪುಟಗಳನ್ನು ತಿರುಗಿಸಿ',
            'compress': 'PDF ಸಂಕುಚಿಸಿ',
            'pdf_to_word': 'PDF ನಿಂದ Word ಗೆ',
            'word_to_pdf': 'Word ನಿಂದ PDF ಗೆ',
            'pdf_to_jpeg': 'PDF ನಿಂದ JPEG ಗೆ',
            'jpeg_to_pdf': 'JPEG ನಿಂದ PDF ಗೆ'
        };

        return titles[operation] || operation;
    }

    getOperationForm(operation) {
        let form = `
            <div id="uploadArea" class="upload-area">
                <span class="upload-icon">📁</span>
                <div class="upload-text">${this.messages.dragFiles}</div>
                <div class="upload-subtext">${this.messages.clickToSelect}</div>
                <input type="file" id="fileInput" style="display: none;" multiple>
            </div>
            <div id="fileList" class="file-list"></div>
        `;

        // Add operation-specific inputs
        if (['split', 'extract', 'delete'].includes(operation)) {
            form += `
                <div class="form-group">
                    <label class="form-label">ಪುಟ ಸಂಖ್ಯೆಗಳು (ಉದಾ: 1-3,5,7-9):</label>
                    <input type="text" id="pages" class="form-input" placeholder="1-3,5,7-9">
                    <small class="form-help">ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ಕಾಮಾಗಳಿಂದ ಪ್ರತ್ಯೇಕಿಸಿ</small>
                </div>
            `;
        }

        if (operation === 'rotate') {
            form += `
                <div class="form-group">
                    <label class="form-label">ತಿರುಗಿಸುವ ಕೋನ:</label>
                    <select id="angle" class="form-select">
                        <option value="90">90° (ಬಲಕ್ಕೆ)</option>
                        <option value="180">180° (ತಲೆಕೆಳಗು)</option>
                        <option value="270">270° (ಎಡಕ್ಕೆ)</option>
                        <option value="-90">-90° (ಎಡಕ್ಕೆ)</option>
                    </select>
                </div>
            `;
        }

        if (operation === 'compress') {
            form += `
                <div class="form-group">
                    <label class="form-label">ಸಂಕುಚನ ಗುಣಮಟ್ಟ:</label>
                    <select id="quality" class="form-select">
                        <option value="low">ಕಡಿಮೆ (ದೊಡ್ಡ ಫೈಲ್)</option>
                        <option value="medium" selected>ಮಧ್ಯಮ</option>
                        <option value="high">ಹೆಚ್ಚು (ಚಿಕ್ಕ ಫೈಲ್)</option>
                    </select>
                </div>
            `;
        }

        if (operation === 'crop') {
            form += `
                <div class="form-group">
                    <label class="form-label">ಅಂಚುಗಳು (ಪಾಯಿಂಟ್‌ಗಳಲ್ಲಿ):</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <input type="number" id="left" class="form-input" placeholder="ಎಡ" value="0" min="0">
                        <input type="number" id="top" class="form-input" placeholder="ಮೇಲೆ" value="0" min="0">
                        <input type="number" id="right" class="form-input" placeholder="ಬಲ" value="0" min="0">
                        <input type="number" id="bottom" class="form-input" placeholder="ಕೆಳಗೆ" value="0" min="0">
                    </div>
                    <small class="form-help">ಕತ್ತರಿಸಬೇಕಾದ ಅಂಚುಗಳ ಮಾಪನ</small>
                </div>
            `;
        }

        form += `
            <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                <button id="processBtn" class="btn btn-primary" disabled>
                    ${this.messages.selectFiles}
                </button>
                <button id="clearFiles" class="btn">${this.messages.clear}</button>
            </div>
        `;

        return form;
    }

    showProcessingModal() {
        const modal = document.getElementById('uploadModal');
        const content = document.getElementById('modalContent');

        content.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div class="spinner"></div>
                <h3>${this.messages.processing}</h3>
                <div class="progress-container">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <p id="progressText">ಆರಂಭಿಸುತ್ತಿದೆ...</p>
            </div>
        `;

        // Start progress animation
        this.animateProgress();
    }

    animateProgress() {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (!progressBar) return;

        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 90) {
                progress = 90;
                clearInterval(interval);
            }
            
            progressBar.style.width = progress + '%';
            
            if (progressText) {
                if (progress < 30) {
                    progressText.textContent = 'ಫೈಲ್‌ಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡುತ್ತಿದೆ...';
                } else if (progress < 60) {
                    progressText.textContent = 'ಪ್ರಕ್ರಿಯೆ ನಡೆಯುತ್ತಿದೆ...';
                } else {
                    progressText.textContent = 'ಪೂರ್ಣಗೊಳಿಸುತ್ತಿದೆ...';
                }
            }
        }, 500);
    }

    showSuccessModal(result) {
        const modal = document.getElementById('uploadModal');
        const content = document.getElementById('modalContent');

        content.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div class="success-icon">✅</div>
                <h3>${this.messages.completed}</h3>
                <p>${this.messages.downloadReady}</p>
                <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;">
                    <a href="${result.download_url}" class="btn btn-primary" download>
                        ${this.messages.download}
                    </a>
                    <button class="btn" onclick="kannadaPDF.closeModal()">
                        ${this.messages.close}
                    </button>
                </div>
            </div>
        `;

        // Auto-download if single file
        if (result.auto_download) {
            setTimeout(() => {
                const link = document.createElement('a');
                link.href = result.download_url;
                link.download = result.filename || 'processed_file';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }, 1000);
        }
    }

    showErrorModal(errorMessage) {
        const modal = document.getElementById('uploadModal');
        const content = document.getElementById('modalContent');

        // Localize common error messages
        let localizedError = errorMessage;
        if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
            localizedError = this.messages.networkError;
        } else if (errorMessage.includes('500') || errorMessage.includes('server')) {
            localizedError = this.messages.serverError;
        }

        content.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div class="error-icon">❌</div>
                <h3>${this.messages.error}</h3>
                <p>${localizedError}</p>
                <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;">
                    <button class="btn btn-primary" onclick="kannadaPDF.retryOperation()">
                        ${this.messages.retry}
                    </button>
                    <button class="btn" onclick="kannadaPDF.closeModal()">
                        ${this.messages.close}
                    </button>
                </div>
            </div>
        `;
    }

    retryOperation() {
        if (this.currentOperation && this.selectedFiles.length > 0) {
            this.processFiles();
        } else {
            this.showUploadModal(this.currentOperation);
        }
    }

    closeModal() {
        const modal = document.getElementById('uploadModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('fade-in');
        }
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} fade-in`;
        alert.innerHTML = `
            <span>${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
        `;

        // Add to page
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alert, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Utility method for debugging
    log(message, data = null) {
        if (window.console && console.log) {
            console.log(`[KannadaPDF] ${message}`, data);
        }
    }

    // Method to handle browser back/forward
    handleBrowserNavigation() {
        window.addEventListener('popstate', () => {
            this.closeModal();
        });
    }

    // Initialize theme handling
    initializeTheme() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        const updateTheme = (e) => {
            document.body.setAttribute('data-theme', e.matches ? 'dark' : 'light');
        };
        
        updateTheme(prefersDark);
        prefersDark.addEventListener('change', updateTheme);
    }

    // Method to clean up resources
    destroy() {
        this.selectedFiles = [];
        this.currentOperation = null;
        this.sessionId = null;
        
        // Remove event listeners
        document.querySelectorAll('.operation-btn').forEach(btn => {
            btn.removeEventListener('click', this.selectOperation);
        });
    }
}

// Initialize the toolkit when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.kannadaPDF = new KannadaPDFToolkit();
    
    // Handle browser navigation
    window.kannadaPDF.handleBrowserNavigation();
    
    // Initialize theme
    window.kannadaPDF.initializeTheme();
});

// Handle page unload
window.addEventListener('beforeunload', function() {
    if (window.kannadaPDF) {
        window.kannadaPDF.destroy();
    }
});