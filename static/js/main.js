document.addEventListener('DOMContentLoaded', function() {
    let selectedFiles = [];
    let currentOperation = '';
    let currentPreviewData = null;
    let selectedPages = new Set();

    const operationConfigs = {
        'merge': {
            title: 'PDF ಗಳನ್ನು ವಿಲೀನಗೊಳಿಸಿ',
            accept: '.pdf',
            supportText: 'PDF ಫೈಲ್‌ಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ (ಕನಿಷ್ಠ 2 ಫೈಲ್‌ಗಳು)',
            multiple: true,
            options: [],
            minFiles: 2,
            hasPreview: false
        },
        'split': {
            title: 'PDF ಅನ್ನು ವಿಭಾಗಿಸಿ',
            accept: '.pdf',
            supportText: 'ಒಂದು PDF ಫೈಲ್ ಮಾತ್ರ',
            multiple: false,
            options: ['pages'],
            minFiles: 1,
            hasPreview: true
        },
        'extract': {
            title: 'ಪುಟಗಳನ್ನು ಹೊರತೆಗೆಯಿರಿ',
            accept: '.pdf',
            supportText: 'ಒಂದು PDF ಫೈಲ್ ಮಾತ್ರ',
            multiple: false,
            options: ['pages'],
            minFiles: 1,
            hasPreview: true
        },
        'delete': {
            title: 'ಪುಟಗಳನ್ನು ಅಳಿಸಿ',
            accept: '.pdf',
            supportText: 'ಒಂದು PDF ಫೈಲ್ ಮಾತ್ರ',
            multiple: false,
            options: ['pages'],
            minFiles: 1,
            hasPreview: true
        },
        'compress': {
            title: 'PDF ಸಂಕುಚಿಸಿ',
            accept: '.pdf',
            supportText: 'PDF ಫೈಲ್‌ಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ',
            multiple: true,
            options: ['compression'],
            minFiles: 1,
            hasPreview: false
        },
        'pdf_to_jpeg': {
            title: 'PDF ನಿಂದ JPEG',
            accept: '.pdf',
            supportText: 'PDF ಫೈಲ್‌ಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ',
            multiple: true,
            options: [],
            minFiles: 1,
            hasPreview: false
        },
        'jpeg_to_pdf': {
            title: 'JPEG ನಿಂದ PDF',
            accept: '.jpg,.jpeg,.png,.bmp,.tiff',
            supportText: 'ಚಿತ್ರ ಫೈಲ್‌ಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ',
            multiple: true,
            options: [],
            minFiles: 1,
            hasPreview: false
        },
        'pdf_to_word': {
            title: 'PDF ನಿಂದ Word',
            accept: '.pdf',
            supportText: 'ಒಂದು PDF ಫೈಲ್ ಮಾತ್ರ',
            multiple: false,
            options: [],
            minFiles: 1,
            hasPreview: false
        },
        'word_to_pdf': {
            title: 'Word ನಿಂದ PDF',
            accept: '.docx,.doc',
            supportText: 'Word ಫೈಲ್‌ಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ',
            multiple: true,
            options: [],
            minFiles: 1,
            hasPreview: false
        }
    };

    // Global functions
    window.selectOperation = function(operation) {
        currentOperation = operation;
        const config = operationConfigs[operation];
        
        document.getElementById('modalTitle').textContent = config.title;
        document.getElementById('selectedOperation').value = operation;
        document.getElementById('fileInput').accept = config.accept;
        document.getElementById('fileInput').multiple = config.multiple;
        document.getElementById('uploadSubtext').textContent = config.supportText;
        
        showOperationOptions(config.options, config.hasPreview);
        resetModalForm();
        restoreOriginalModalContent();
        document.getElementById('operationModal').style.display = 'block';
    };

    window.closeModal = function() {
        document.getElementById('operationModal').style.display = 'none';
        document.getElementById('loadingModal').style.display = 'none';
        resetModalForm();
    };

    window.closePreviewModal = function() {
        document.getElementById('previewModal').style.display = 'none';
        currentPreviewData = null;
        selectedPages.clear();
    };

    window.removeFile = function(index) {
        selectedFiles.splice(index, 1);
        displaySelectedFiles();
        updateProcessButton();
        updatePreviewSection();
        
        const dt = new DataTransfer();
        selectedFiles.forEach(file => dt.items.add(file));
        document.getElementById('fileInput').files = dt.files;
    };

    // Preview functions
    window.showPagePreview = async function() {
        if (selectedFiles.length === 0) {
            showAlert('error', 'ದಯವಿಟ್ಟು ಮೊದಲು PDF ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ');
            return;
        }

        const loadingPreview = document.getElementById('loadingPreview');
        const pagesGrid = document.getElementById('pagesGrid');
        
        document.getElementById('previewModal').style.display = 'block';
        loadingPreview.style.display = 'block';
        pagesGrid.innerHTML = '';
        selectedPages.clear();
        updateSelectedPagesDisplay();

        try {
            const formData = new FormData();
            formData.append('file', selectedFiles[0]);

            const response = await fetch('/generate-preview', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                currentPreviewData = result;
                displayPagePreviews(result);
            } else {
                throw new Error(result.error || 'ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ');
            }
        } catch (error) {
            console.error('Preview generation error:', error);
            showAlert('error', 'ಪೂರ್ವವೀಕ್ಷಣೆ ಲೋಡ್ ಮಾಡಲಾಗಲಿಲ್ಲ: ' + error.message);
            closePreviewModal();
        } finally {
            loadingPreview.style.display = 'none';
        }
    };

    window.togglePageSelection = function(pageNum) {
        const pageDiv = document.querySelector(`[data-page-num="${pageNum}"]`);
        const checkbox = pageDiv.querySelector('.page-checkbox');

        if (selectedPages.has(pageNum)) {
            selectedPages.delete(pageNum);
            pageDiv.classList.remove('selected');
            checkbox.checked = false;
        } else {
            selectedPages.add(pageNum);
            pageDiv.classList.add('selected');
            checkbox.checked = true;
        }

        updateSelectedPagesDisplay();
    };

    window.selectAllPages = function() {
        if (!currentPreviewData) return;

        currentPreviewData.previews.forEach(preview => {
            selectedPages.add(preview.page_num);
            const pageDiv = document.querySelector(`[data-page-num="${preview.page_num}"]`);
            const checkbox = pageDiv.querySelector('.page-checkbox');
            pageDiv.classList.add('selected');
            checkbox.checked = true;
        });

        updateSelectedPagesDisplay();
    };

    window.clearSelection = function() {
        selectedPages.clear();
        document.querySelectorAll('.page-thumbnail').forEach(pageDiv => {
            pageDiv.classList.remove('selected');
            const checkbox = pageDiv.querySelector('.page-checkbox');
            checkbox.checked = false;
        });
        updateSelectedPagesDisplay();
    };

    window.switchSelectionMethod = function(method) {
        const tabs = document.querySelectorAll('.method-tab');
        const contents = document.querySelectorAll('.method-content');

        tabs.forEach(tab => tab.classList.remove('active'));
        contents.forEach(content => content.classList.remove('active'));

        if (method === 'visual') {
            tabs[0].classList.add('active');
            document.getElementById('visualMethod').classList.add('active');
        } else {
            tabs[1].classList.add('active');
            document.getElementById('manualMethod').classList.add('active');
        }
    };

    window.applyManualSelection = function() {
        const input = document.getElementById('manualPagesInput');
        const pagesStr = input.value.trim();

        if (!pagesStr || !currentPreviewData) return;

        clearSelection();

        try {
            const pageNumbers = parsePageRanges(pagesStr, currentPreviewData.total_pages);
            pageNumbers.forEach(pageNum => {
                if (pageNum >= 1 && pageNum <= currentPreviewData.total_pages) {
                    selectedPages.add(pageNum);
                    const pageDiv = document.querySelector(`[data-page-num="${pageNum}"]`);
                    if (pageDiv) {
                        const checkbox = pageDiv.querySelector('.page-checkbox');
                        pageDiv.classList.add('selected');
                        checkbox.checked = true;
                    }
                }
            });

            updateSelectedPagesDisplay();
        } catch (error) {
            showAlert('error', 'ಅಮಾನ್ಯ ಪುಟ ಸಂಖ್ಯೆಗಳು: ' + error.message);
        }
    };

    window.confirmPageSelection = function() {
        if (selectedPages.size === 0) {
            showAlert('error', 'ದಯವಿಟ್ಟು ಕನಿಷ್ಠ ಒಂದು ಪುಟವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ');
            return;
        }

        const sortedPages = Array.from(selectedPages).sort((a, b) => a - b);
        const pagesStr = formatPageRanges(sortedPages);

        // Update the pages input in the main modal
        const pagesInput = document.getElementById('pagesInput');
        if (pagesInput) {
            pagesInput.value = pagesStr;
        }

        // Store selected pages in hidden input
        const selectedPagesInput = document.getElementById('selectedPagesInput');
        if (selectedPagesInput) {
            selectedPagesInput.value = pagesStr;
        }

        closePreviewModal();
        showAlert('success', `${selectedPages.size} ಪುಟಗಳು ಆಯ್ಕೆಯಾಗಿವೆ: ${pagesStr}`);
    };

    function displayPagePreviews(previewData) {
        const pagesGrid = document.getElementById('pagesGrid');
        pagesGrid.innerHTML = '';

        previewData.previews.forEach((preview, index) => {
            const pageDiv = document.createElement('div');
            pageDiv.className = 'page-thumbnail';
            pageDiv.dataset.pageNum = preview.page_num;

            pageDiv.innerHTML = `
                <img src="${preview.image_path}" alt="Page ${preview.page_num}" class="page-image" loading="lazy">
                <div class="page-number">ಪುಟ ${preview.page_num}</div>
                <input type="checkbox" class="page-checkbox" onchange="togglePageSelection(${preview.page_num})">
            `;

            pageDiv.addEventListener('click', function(e) {
                if (e.target.type !== 'checkbox') {
                    togglePageSelection(preview.page_num);
                }
            });

            pagesGrid.appendChild(pageDiv);
        });
    }

    function updateSelectedPagesDisplay() {
        const count = selectedPages.size;
        const countElement = document.getElementById('selectedPagesCount');
        if (countElement) {
            countElement.textContent = `${count} ಪುಟಗಳು ಆಯ್ಕೆಯಾಗಿವೆ`;
        }

        const confirmBtn = document.getElementById('confirmSelectionBtn');
        if (confirmBtn) {
            confirmBtn.disabled = count === 0;
        }
    }

    // File handling functions
    function displaySelectedFiles() {
        const fileList = document.getElementById('selectedFilesList');
        if (!fileList) return;

        if (selectedFiles.length === 0) {
            fileList.innerHTML = '<p class="no-files">ಯಾವುದೇ ಫೈಲ್‌ಗಳು ಆಯ್ಕೆಯಾಗಿಲ್ಲ</p>';
            return;
        }

        fileList.innerHTML = selectedFiles.map((file, index) => `
            <div class="file-item">
                <div class="file-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                </div>
                <button type="button" class="remove-file-btn" onclick="removeFile(${index})" title="ಫೈಲ್ ತೆಗೆದುಹಾಕಿ">
                    ✕
                </button>
            </div>
        `).join('');
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function updateProcessButton() {
        const processBtn = document.getElementById('processBtn');
        const config = operationConfigs[currentOperation];
        
        if (processBtn && config) {
            processBtn.disabled = selectedFiles.length < config.minFiles;
        }
    }

    function updatePreviewSection() {
        const previewSection = document.getElementById('previewSection');
        const config = operationConfigs[currentOperation];
        
        if (previewSection) {
            previewSection.style.display = (config?.hasPreview && selectedFiles.length > 0) ? 'block' : 'none';
        }
    }

    function showOperationOptions(options, hasPreview) {
        const optionsDiv = document.getElementById('operationOptions');
        const previewSection = document.getElementById('previewSection');
        
        // Clear existing options
        optionsDiv.innerHTML = '';
        
        // Show/hide preview section
        if (previewSection) {
            previewSection.style.display = hasPreview ? 'block' : 'none';
        }

        options.forEach(option => {
            if (option === 'pages') {
                optionsDiv.innerHTML += `
                    <div class="option-group">
                        <label for="pagesInput">ಪುಟಗಳು (ಉದಾ: 1-3,5,7-9):</label>
                        <input type="text" id="pagesInput" name="pages" placeholder="1-3,5,7-9">
                        <input type="hidden" id="selectedPagesInput" name="selected_pages">
                    </div>
                `;
            } else if (option === 'compression') {
                optionsDiv.innerHTML += `
                    <div class="option-group">
                        <label for="compressionLevel">ಸಂಕುಚನ ಮಟ್ಟ:</label>
                        <select id="compressionLevel" name="compression_level">
                            <option value="low">ಕಡಿಮೆ</option>
                            <option value="medium" selected>ಮಧ್ಯಮ</option>
                            <option value="high">ಹೆಚ್ಚಿನ</option>
                        </select>
                    </div>
                `;
            }
        });
    }

    function resetModalForm() {
        selectedFiles = [];
        selectedPages.clear();
        currentPreviewData = null;
        
        const fileInput = document.getElementById('fileInput');
        if (fileInput) fileInput.value = '';
        
        const pagesInput = document.getElementById('pagesInput');
        if (pagesInput) pagesInput.value = '';
        
        const selectedPagesInput = document.getElementById('selectedPagesInput');
        if (selectedPagesInput) selectedPagesInput.value = '';
        
        displaySelectedFiles();
        updateProcessButton();
        updatePreviewSection();
    }

    function restoreOriginalModalContent() {
        const modalBody = document.querySelector('.modal-body');
        const uploadArea = document.getElementById('uploadArea');
        const filesList = document.getElementById('selectedFilesList');
        const processBtn = document.getElementById('processBtn');
        
        if (uploadArea) uploadArea.style.display = 'block';
        if (filesList) filesList.style.display = 'block';
        if (processBtn) processBtn.style.display = 'inline-block';
        
        const modalFooter = document.querySelector('.modal-footer');
        if (modalFooter) modalFooter.style.display = 'flex';
    }

    // Page range parsing and formatting utilities
    function parsePageRanges(pagesStr, totalPages) {
        const pages = new Set();
        const parts = pagesStr.split(',');
        
        for (let part of parts) {
            part = part.trim();
            if (part.includes('-')) {
                const [start, end] = part.split('-').map(s => parseInt(s.trim()));
                if (isNaN(start) || isNaN(end) || start < 1 || end > totalPages || start > end) {
                    throw new Error(`ಅಮಾನ್ಯ ಶ್ರೇಣಿ: ${part}`);
                }
                for (let i = start; i <= end; i++) {
                    pages.add(i);
                }
            } else {
                const pageNum = parseInt(part);
                if (isNaN(pageNum) || pageNum < 1 || pageNum > totalPages) {
                    throw new Error(`ಅಮಾನ್ಯ ಪುಟ ಸಂಖ್ಯೆ: ${part}`);
                }
                pages.add(pageNum);
            }
        }
        
        return Array.from(pages);
    }

    function formatPageRanges(pageNumbers) {
        if (pageNumbers.length === 0) return '';
        
        const sorted = [...pageNumbers].sort((a, b) => a - b);
        const ranges = [];
        let start = sorted[0];
        let end = sorted[0];
        
        for (let i = 1; i < sorted.length; i++) {
            if (sorted[i] === end + 1) {
                end = sorted[i];
            } else {
                if (start === end) {
                    ranges.push(start.toString());
                } else {
                    ranges.push(`${start}-${end}`);
                }
                start = end = sorted[i];
            }
        }
        
        if (start === end) {
            ranges.push(start.toString());
        } else {
            ranges.push(`${start}-${end}`);
        }
        
        return ranges.join(',');
    }

    // Alert system
    function showAlert(type, message) {
        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <span class="alert-message">${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
        `;

        alertContainer.appendChild(alert);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }

    // File input event handlers
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            const config = operationConfigs[currentOperation];
            
            if (config.multiple) {
                selectedFiles = files;
            } else {
                selectedFiles = files.slice(0, 1);
            }
            
            displaySelectedFiles();
            updateProcessButton();
            updatePreviewSection();
        });
    }

    // Form submission handler
    const operationForm = document.getElementById('operationForm');
    if (operationForm) {
        operationForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (selectedFiles.length === 0) {
                showAlert('error', 'ದಯವಿಟ್ಟು ಕನಿಷ್ಠ ಒಂದು ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ');
                return;
            }

            const config = operationConfigs[currentOperation];
            if (selectedFiles.length < config.minFiles) {
                showAlert('error', `ಈ ಕಾರ್ಯಾಚರಣೆಗೆ ಕನಿಷ್ಠ ${config.minFiles} ಫೈಲ್‌ಗಳು ಬೇಕಾಗುತ್ತವೆ`);
                return;
            }

            // Show loading modal
            document.getElementById('operationModal').style.display = 'none';
            document.getElementById('loadingModal').style.display = 'block';

            try {
                const formData = new FormData();
                formData.append('operation', currentOperation);
                
                selectedFiles.forEach(file => {
                    formData.append('files', file);
                });

                // Add operation-specific parameters
                const pagesInput = document.getElementById('pagesInput');
                if (pagesInput && pagesInput.value.trim()) {
                    formData.append('pages', pagesInput.value.trim());
                }

                const compressionLevel = document.getElementById('compressionLevel');
                if (compressionLevel) {
                    formData.append('compression_level', compressionLevel.value);
                }

                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    // Handle successful processing
                    if (result.download_url) {
                        showAlert('success', 'ಕಾರ್ಯಾಚರಣೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!');
                        
                        // Create download link
                        const downloadLink = document.createElement('a');
                        downloadLink.href = result.download_url;
                        downloadLink.download = result.filename || 'processed_file';
                        document.body.appendChild(downloadLink);
                        downloadLink.click();
                        document.body.removeChild(downloadLink);
                    } else {
                        showAlert('success', result.message || 'ಕಾರ್ಯಾಚರಣೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!');
                    }
                } else {
                    throw new Error(result.error || 'ಕಾರ್ಯಾಚರಣೆ ವಿಫಲವಾಗಿದೆ');
                }
            } catch (error) {
                showAlert('error', 'ದೋಷ: ' + error.message);
            } finally {
                document.getElementById('loadingModal').style.display = 'none';
                resetModalForm();
            }
        });
    }

    // Drag and drop functionality
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            uploadArea.classList.add('drag-over');
        }

        function unhighlight(e) {
            uploadArea.classList.remove('drag-over');
        }

        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = Array.from(dt.files);
            const config = operationConfigs[currentOperation];

            if (config.multiple) {
                selectedFiles = files;
            } else {
                selectedFiles = files.slice(0, 1);
            }

            // Update file input
            const fileInput = document.getElementById('fileInput');
            const dataTransfer = new DataTransfer();
            selectedFiles.forEach(file => dataTransfer.items.add(file));
            fileInput.files = dataTransfer.files;

            displaySelectedFiles();
            updateProcessButton();
            updatePreviewSection();
        }
    }

    // Modal event handlers
    window.addEventListener('click', function(e) {
        const operationModal = document.getElementById('operationModal');
        const previewModal = document.getElementById('previewModal');
        const loadingModal = document.getElementById('loadingModal');

        if (e.target === operationModal) {
            closeModal();
        }
        if (e.target === previewModal) {
            closePreviewModal();
        }
        if (e.target === loadingModal) {
            // Don't close loading modal on click
        }
    });

    // Keyboard event handlers
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const operationModal = document.getElementById('operationModal');
            const previewModal = document.getElementById('previewModal');
            
            if (operationModal.style.display === 'block') {
                closeModal();
            } else if (previewModal.style.display === 'block') {
                closePreviewModal();
            }
        }
    });
});