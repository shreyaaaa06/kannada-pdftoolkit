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
            options: ['split_method', 'pages'],
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
        },
        'compare': {
            title: 'PDF ಫೈಲ್‌ಗಳನ್ನು ಹೋಲಿಸಿ',
            accept: '.pdf',
            supportText: 'ಹೋಲಿಕೆಗಾಗಿ ನಿಖರವಾಗಿ 2 PDF ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ',
            multiple: true,
            options: ['compareType'],
            minFiles: 2,
            maxFiles: 2,
            hasPreview: false
        },
        'rotate': {
            title: 'PDF ತಿರುಗಿಸಿ',
            accept: '.pdf',
            supportText: 'ಒಂದು PDF ಫೈಲ್ ಮಾತ್ರ',
            multiple: false,
            options: ['rotation_angle', 'pages', 'apply_to_all'],
            minFiles: 1,
            hasPreview: true
        }
    };

    // CRITICAL FIX: Complete modal reset function
    function completeModalReset() {
        console.log('=== COMPLETE MODAL RESET START ===');
        
        // Reset all state variables
        selectedFiles = [];
        currentOperation = '';
        currentPreviewData = null;
        selectedPages.clear();
        
        // Close any open modals
        document.getElementById('operationModal').style.display = 'none';
        document.getElementById('previewModal').style.display = 'none';
        document.getElementById('loadingModal').style.display = 'none';
        
        console.log('=== COMPLETE MODAL RESET END ===');
    }

    // CRITICAL FIX: Safe element finder with error handling
    function safeGetElement(id) {
        const element = document.getElementById(id);
        if (!element) {
            console.warn(`Element with ID '${id}' not found`);
        }
        return element;
    }

    // CRITICAL FIX: Safe property setter
    function safeSetProperty(elementId, property, value) {
        const element = safeGetElement(elementId);
        if (element && element[property] !== undefined) {
            element[property] = value;
            return true;
        } else {
            console.warn(`Cannot set ${property} on element '${elementId}'`);
            return false;
        }
    }

    // CRITICAL FIX: Safe text content setter
    function safeSetTextContent(elementId, content) {
        const element = safeGetElement(elementId);
        if (element) {
            element.textContent = content;
            return true;
        }
        return false;
    }

    // Global functions with safety checks
    window.selectOperation = function(operation) {
        console.log(`=== SELECTING OPERATION: ${operation} ===`);
        
        try {
            // Force complete reset first
            completeModalReset();
            
            // Small delay to ensure DOM is ready
            setTimeout(() => {
                currentOperation = operation;
                const config = operationConfigs[operation];
                
                if (!config) {
                    console.error(`Unknown operation: ${operation}`);
                    return;
                }
                
                // Restore original modal content BEFORE setting values
                restoreOriginalModalContent();
                
                // Small delay to ensure DOM elements are created
                setTimeout(() => {
                    // Now safely set the values
                    safeSetTextContent('modalTitle', config.title);
                    safeSetProperty('selectedOperation', 'value', operation);
                    safeSetProperty('fileInput', 'accept', config.accept);
                    safeSetProperty('fileInput', 'multiple', config.multiple);
                    safeSetTextContent('uploadSubtext', config.supportText);
                    
                    // Show operation options and update UI
                    showOperationOptions(config.options, config.hasPreview);
                    resetModalForm();
                    
                    // Show the modal
                    const modal = safeGetElement('operationModal');
                    if (modal) {
                        modal.style.display = 'block';
                    }
                }, 50);
            }, 50);
            
        } catch (error) {
            console.error('Error in selectOperation:', error);
            // Fallback: just show the modal with default content
            const modal = safeGetElement('operationModal');
            if (modal) {
                restoreOriginalModalContent();
                modal.style.display = 'block';
            }
        }
    };

    window.closeModal = function() {
        console.log('Closing modal and resetting state');
        completeModalReset();
    };

    window.closePreviewModal = function() {
        const previewModal = safeGetElement('previewModal');
        if (previewModal) {
            previewModal.style.display = 'none';
        }
        currentPreviewData = null;
        selectedPages.clear();
    };

    window.removeFile = function(index) {
        if (index >= 0 && index < selectedFiles.length) {
            selectedFiles.splice(index, 1);
            displaySelectedFiles();
            updateProcessButton();
            updatePreviewSection();
            
            // Update file input
            try {
                const fileInput = safeGetElement('fileInput');
                if (fileInput) {
                    const dt = new DataTransfer();
                    selectedFiles.forEach(file => dt.items.add(file));
                    fileInput.files = dt.files;
                }
            } catch (error) {
                console.warn('Could not update file input:', error);
            }
        }
    };

    // Compression functions
    window.updateCompressionUI = function() {
        const compressionSelect = safeGetElement('compressionSelect');
        const targetSizeGroup = safeGetElement('targetSizeGroup');
        const advancedToggle = safeGetElement('advancedToggle');
        
        if (!compressionSelect) return;
        
        const selectedValue = compressionSelect.value;
        
        if (selectedValue === 'custom') {
            if (targetSizeGroup) targetSizeGroup.style.display = 'block';
            if (advancedToggle) advancedToggle.style.display = 'none';
            
            const advancedOptions = safeGetElement('advancedCompressionOptions');
            if (advancedOptions) advancedOptions.style.display = 'none';
            
            const showAdvancedComp = safeGetElement('showAdvancedComp');
            if (showAdvancedComp) showAdvancedComp.checked = false;
        } else {
            if (targetSizeGroup) targetSizeGroup.style.display = 'none';
            if (advancedToggle) advancedToggle.style.display = 'block';
        }
    };

    window.toggleAdvancedCompression = function() {
        const showAdvancedComp = safeGetElement('showAdvancedComp');
        const advancedOptions = safeGetElement('advancedCompressionOptions');
        
        if (showAdvancedComp && advancedOptions) {
            advancedOptions.style.display = showAdvancedComp.checked ? 'block' : 'none';
        }
    };

    window.updateQualityDisplay = function() {
        const imageQuality = safeGetElement('imageQuality');
        const qualityValue = safeGetElement('qualityValue');
        
        if (imageQuality && qualityValue) {
            qualityValue.textContent = imageQuality.value + '%';
        }
    };

    // Split method handling
    window.handleSplitMethodChange = function() {
        const splitMethodSelect = safeGetElement('splitMethodSelect');
        const method = splitMethodSelect ? splitMethodSelect.value : 'pages';
        
        const pagesGroup = safeGetElement('pagesGroup');
        const fileSizeGroup = safeGetElement('fileSizeGroup');
        const autoChunkGroup = safeGetElement('autoChunkGroup');
        const pagesInput = safeGetElement('pagesInput');
        const previewSection = safeGetElement('previewSection');
        
        // Hide all method-specific groups first
        if (pagesGroup) pagesGroup.style.display = 'none';
        if (fileSizeGroup) fileSizeGroup.style.display = 'none';
        if (autoChunkGroup) autoChunkGroup.style.display = 'none';
        
        if (method === 'size') {
            if (fileSizeGroup) fileSizeGroup.style.display = 'block';
            if (pagesInput) pagesInput.placeholder = 'ಗಾತ್ರದ ಆಧಾರದ ಮೇಲೆ ಸ್ವಯಂಚಾಲಿತವಾಗಿ ವಿಭಾಗಿಸಲಾಗುವುದು';
            if (previewSection) previewSection.style.display = 'none';
        } else if (method === 'auto') {
            if (autoChunkGroup) autoChunkGroup.style.display = 'block';
            if (pagesInput) pagesInput.placeholder = 'ಸ್ವಯಂಚಾಲಿತ ಚಂಕಿಂಗ್';
            if (previewSection) previewSection.style.display = 'none';
        } else { // method === 'pages'
            if (pagesGroup) pagesGroup.style.display = 'block';
            if (pagesInput) pagesInput.placeholder = 'ಉದಾ: 1,3,5-10 ಅಥವಾ 1-10,15-25';
        }
    };

    // Preview functions
    window.showPagePreview = async function() {
        if (selectedFiles.length === 0) {
            showAlert('error', 'ದಯವಿಟ್ಟು ಮೊದಲು PDF ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ');
            return;
        }

        const loadingPreview = safeGetElement('loadingPreview');
        const pagesGrid = safeGetElement('pagesGrid');
        const previewModal = safeGetElement('previewModal');
        
        if (previewModal) previewModal.style.display = 'block';
        if (loadingPreview) loadingPreview.style.display = 'block';
        if (pagesGrid) pagesGrid.innerHTML = '';
        
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
            if (loadingPreview) loadingPreview.style.display = 'none';
        }
    };

    window.togglePageSelection = function(pageNum) {
        const pageDiv = document.querySelector(`[data-page-num="${pageNum}"]`);
        if (!pageDiv) return;
        
        const checkbox = pageDiv.querySelector('.page-checkbox');

        if (selectedPages.has(pageNum)) {
            selectedPages.delete(pageNum);
            pageDiv.classList.remove('selected');
            if (checkbox) checkbox.checked = false;
        } else {
            selectedPages.add(pageNum);
            pageDiv.classList.add('selected');
            if (checkbox) checkbox.checked = true;
        }

        updateSelectedPagesDisplay();
    };

    window.selectAllPages = function() {
        if (!currentPreviewData) return;

        currentPreviewData.previews.forEach(preview => {
            selectedPages.add(preview.page_num);
            const pageDiv = document.querySelector(`[data-page-num="${preview.page_num}"]`);
            if (pageDiv) {
                const checkbox = pageDiv.querySelector('.page-checkbox');
                pageDiv.classList.add('selected');
                if (checkbox) checkbox.checked = true;
            }
        });

        updateSelectedPagesDisplay();
    };

    window.clearSelection = function() {
        selectedPages.clear();
        document.querySelectorAll('.page-thumbnail').forEach(pageDiv => {
            pageDiv.classList.remove('selected');
            const checkbox = pageDiv.querySelector('.page-checkbox');
            if (checkbox) checkbox.checked = false;
        });
        updateSelectedPagesDisplay();
    };

    window.switchSelectionMethod = function(method) {
        const tabs = document.querySelectorAll('.method-tab');
        const contents = document.querySelectorAll('.method-content');

        tabs.forEach(tab => tab.classList.remove('active'));
        contents.forEach(content => content.classList.remove('active'));

        if (method === 'visual') {
            if (tabs[0]) tabs[0].classList.add('active');
            const visualMethod = safeGetElement('visualMethod');
            if (visualMethod) visualMethod.classList.add('active');
        } else {
            if (tabs[1]) tabs[1].classList.add('active');
            const manualMethod = safeGetElement('manualMethod');
            if (manualMethod) manualMethod.classList.add('active');
        }
    };

    window.applyManualSelection = function() {
        const input = safeGetElement('manualPagesInput');
        if (!input || !currentPreviewData) return;
        
        const pagesStr = input.value.trim();
        if (!pagesStr) return;

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
                        if (checkbox) checkbox.checked = true;
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
        const pagesInput = safeGetElement('pagesInput');
        if (pagesInput) {
            pagesInput.value = pagesStr;
        }

        // Store selected pages in hidden input
        const selectedPagesInput = safeGetElement('selectedPagesInput');
        if (selectedPagesInput) {
            selectedPagesInput.value = pagesStr;
        }

        closePreviewModal();
        showAlert('success', `${selectedPages.size} ಪುಟಗಳು ಆಯ್ಕೆಯಾಗಿವೆ: ${pagesStr}`);
    };

    // CRITICAL FIX: New operation restart function
    window.startNewOperation = function(operation) {
        console.log(`=== STARTING NEW OPERATION: ${operation} ===`);
        
        // Complete reset
        completeModalReset();
        
        // Clear any existing alert messages
        clearAlerts();
        
        // Small delay before starting new operation
        setTimeout(() => {
            selectOperation(operation);
        }, 100);
    };

    // Helper function to clear alert messages
    function clearAlerts() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            if (alert.parentElement) {
                alert.remove();
            }
        });
    }

    function displayPagePreviews(previewData) {
        const pagesGrid = safeGetElement('pagesGrid');
        if (!pagesGrid) return;
        
        pagesGrid.innerHTML = '';

        previewData.previews.forEach((preview, index) => {
            const pageDiv = document.createElement('div');
            pageDiv.className = 'page-thumbnail';
            pageDiv.dataset.pageNum = preview.page_num;

            pageDiv.innerHTML = `
                <img src="${preview.image_path}" alt="Page ${preview.page_num}" class="page-image" loading="lazy"
                     onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjI4MCIgdmlld0JveD0iMCAwIDIwMCAyODAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjgwIiBmaWxsPSIjZjVmMWU4Ii8+Cjx0ZXh0IHg9IjEwMCIgeT0iMTQwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOGI3MzU1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiPkVycm9yPC90ZXh0Pgo8L3N2Zz4K'">
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
        const selectedCount = safeGetElement('selectedCount');
        const selectedPagesList = safeGetElement('selectedPagesList');
        const confirmBtn = safeGetElement('confirmSelectionBtn');

        if (selectedCount) {
            selectedCount.textContent = selectedPages.size;
        }

        if (selectedPagesList) {
            if (selectedPages.size === 0) {
                selectedPagesList.innerHTML = `
                    <div style="text-align: center; color: var(--light-brown); padding: 1rem; font-size: 0.9rem;">
                        ಯಾವುದೇ ಪುಟಗಳು ಆಯ್ಕೆಯಾಗಿಲ್ಲ
                    </div>
                `;
            } else {
                const sortedPages = Array.from(selectedPages).sort((a, b) => a - b);
                selectedPagesList.innerHTML = sortedPages.map(pageNum => `
                    <div class="selected-page-item">
                        <span>ಪುಟ ${pageNum}</span>
                        <span class="remove-page" onclick="togglePageSelection(${pageNum})">
                            <i class="fas fa-times"></i>
                        </span>
                    </div>
                `).join('');
            }
        }

        if (confirmBtn) {
            confirmBtn.disabled = selectedPages.size === 0;
        }
    }

    // File handling functions
    function handleFileSelection(files) {
        const config = operationConfigs[currentOperation];
        if (!config) {
            showAlert('error', 'ಕಾರ್ಯಾಚರಣೆ ಆಯ್ಕೆ ಮಾಡಿ');
            return;
        }
        
        // Special handling for compare operation
        if (currentOperation === 'compare') {
            if (files.length !== 2) {
                showAlert('error', 'ಹೋಲಿಕೆಗಾಗಿ ನಿಖರವಾಗಿ 2 PDF ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ');
                return;
            }
            
            const nonPdfFiles = files.filter(file => !file.name.toLowerCase().endsWith('.pdf'));
            if (nonPdfFiles.length > 0) {
                showAlert('error', 'ಹೋಲಿಕೆಗಾಗಿ ಎರಡೂ ಫೈಲ್‌ಗಳು PDF ಆಗಿರಬೇಕು');
                return;
            }
            
            selectedFiles = files;
        } else {
            // General validation for other operations
            if (!config.multiple && files.length > 1) {
                showAlert('error', 'ಈ ಕಾರ್ಯಾಚರಣೆಗೆ ಒಂದು ಫೈಲ್ ಮಾತ್ರ ಅನುಮತಿಸಲಾಗಿದೆ');
                return;
            }
            
            const validFiles = files.filter(file => {
                const extension = '.' + file.name.split('.').pop().toLowerCase();
                return config.accept.split(',').includes(extension);
            });
            
            if (validFiles.length !== files.length) {
                showAlert('error', 'ಕೆಲವು ಫೈಲ್‌ಗಳು ಬೆಂಬಲಿತವಲ್ಲ');
            }
            
            if (!config.multiple) {
                selectedFiles = validFiles.slice(0, 1);
            } else {
                validFiles.forEach(file => {
                    const existingFile = selectedFiles.find(f => f.name === file.name && f.size === file.size);
                    if (!existingFile) {
                        selectedFiles.push(file);
                    }
                });
            }
        }
        
        displaySelectedFiles();
        updateProcessButton();
        updatePreviewSection();
    }

    function displaySelectedFiles() {
        const fileList = safeGetElement('filesList');
        if (!fileList) return;

        if (selectedFiles.length === 0) {
            fileList.innerHTML = '<p class="no-files">ಯಾವುದೇ ಫೈಲ್‌ಗಳು ಆಯ್ಕೆಯಾಗಿಲ್ಲ</p>';
            fileList.style.display = 'none';
            return;
        }

        fileList.style.display = 'block';
        fileList.innerHTML = selectedFiles.map((file, index) => `
            <div class="file-item">
                <div class="file-icon">
                    <i class="fas fa-file-${getFileIcon(file.name)}"></i>
                </div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
                <div class="file-remove" onclick="removeFile(${index})" title="ಫೈಲ್ ತೆಗೆದುಹಾಕಿ">
                    <i class="fas fa-times"></i>
                </div>
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

    function getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const icons = {
            'pdf': 'pdf', 'doc': 'word', 'docx': 'word',
            'jpg': 'image', 'jpeg': 'image', 'png': 'image',
            'bmp': 'image', 'tiff': 'image'
        };
        return icons[extension] || 'alt';
    }

    function updateProcessButton() {
        const processBtn = safeGetElement('processBtn');
        const config = operationConfigs[currentOperation];
        
        if (processBtn && config) {
            const hasEnoughFiles = selectedFiles.length >= (config.minFiles || 1);
            
            if (hasEnoughFiles) {
                processBtn.disabled = false;
                processBtn.innerHTML = '<i class="fas fa-cog"></i> ಪ್ರಕ್ರಿಯೆ ಮಾಡಿ';
            } else {
                processBtn.disabled = true;
                if (currentOperation === 'merge') {
                    processBtn.innerHTML = '<i class="fas fa-cog"></i> ಕನಿಷ್ಠ 2 PDF ಫೈಲ್‌ಗಳು ಬೇಕು';
                } else {
                    processBtn.innerHTML = '<i class="fas fa-cog"></i> ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ';
                }
            }
        }
    }

    function updatePreviewSection() {
        const previewSection = safeGetElement('previewSection');
        const config = operationConfigs[currentOperation];
        
        if (previewSection && config) {
            previewSection.style.display = (config.hasPreview && selectedFiles.length > 0) ? 'block' : 'none';
        }
    }

    function showOperationOptions(options, hasPreview) {
        const optionGroups = ['pagesGroup', 'compressionGroup', 'compareTypeGroup', 'splitMethodGroup', 
                             'fileSizeGroup', 'autoChunkGroup', 'rotationAngleGroup', 'applyToAllGroup'];
        
        optionGroups.forEach(group => {
            const element = safeGetElement(group);
            if (element) {
                element.style.display = 'none';
            }
        });
        
        const operationOptions = safeGetElement('operationOptions');
        if (operationOptions) {
            if (options.length > 0) {
                operationOptions.style.display = 'block';
                options.forEach(option => {
                    const element = safeGetElement(option + 'Group');
                    if (element) {
                        element.style.display = 'block';
                        if (currentOperation === 'split' && option === 'split_method') {
                            setTimeout(() => handleSplitMethodChange(), 100);
                        }
                    }
                });
            } else {
                operationOptions.style.display = 'none';
            }
        }
    }

    function resetModalForm() {
        selectedFiles = [];
        selectedPages.clear();
        currentPreviewData = null;
        
        const filesList = safeGetElement('filesList');
        const processBtn = safeGetElement('processBtn');
        const fileInput = safeGetElement('fileInput');
        const previewSection = safeGetElement('previewSection');
        
        if (filesList) {
            filesList.style.display = 'none';
            filesList.innerHTML = '';
        }
        if (processBtn) {
            processBtn.disabled = true;
        }
        if (fileInput) {
            fileInput.value = '';
        }
        if (previewSection) {
            previewSection.style.display = 'none';
        }
    }

    // CRITICAL FIX: Enhanced modal content restoration
    function restoreOriginalModalContent() {
        console.log('=== RESTORING ORIGINAL MODAL CONTENT ===');
        
        const modalBody = document.querySelector('#operationModal .modal-body');
        if (!modalBody) {
            console.error('Modal body not found');
            return;
        }
        
        const config = operationConfigs[currentOperation];
        if (!config) {
            console.error('Config not found for operation:', currentOperation);
            return;
        }
        
        modalBody.innerHTML = `
            <form id="operationForm" method="post" action="/upload" enctype="multipart/form-data">
                <input type="hidden" name="operation" id="selectedOperation" value="${currentOperation}">
                <input type="hidden" name="selected_pages" id="selectedPagesInput">
                
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="upload-text">ಫೈಲ್‌ಗಳನ್ನು ಇಲ್ಲಿ ಎಳೆಯಿರಿ ಅಥವಾ ಕ್ಲಿಕ್ ಮಾಡಿ</div>
                    <div class="upload-subtext" id="uploadSubtext">${config.supportText}</div>
                    <input type="file" name="files" id="fileInput" ${config.multiple ? 'multiple' : ''} accept="${config.accept}" style="display: none;">
                </div>

                <div id="filesList" class="file-list" style="display: none;"></div>

                <div id="previewSection" style="display: none; margin-bottom: 1rem;">
                    <button type="button" class="btn btn-primary" id="showPreviewBtn" onclick="showPagePreview()">
                        <i class="fas fa-eye"></i> ಪುಟಗಳನ್ನು ಪೂರ್ವವೀಕ್ಷಿಸಿ ಮತ್ತು ಆಯ್ಕೆ ಮಾಡಿ
                    </button>
                </div>

                <div id="operationOptions" style="display: none;">
                    <div class="form-group" id="pagesGroup" style="display: none;">
                        <label class="form-label" for="pagesInput">ಪುಟ ಸಂಖ್ಯೆಗಳು</label>
                        <input type="text" name="pages" id="pagesInput" class="form-input" 
                            placeholder="ಉದಾ: 1,3,5-10">
                        <small>ಉದಾ: 1,3,5-10 (ಪ್ರತ್ಯೇಕ ಪುಟಗಳು ಮತ್ತು ವ್ಯಾಪ್ತಿಗಳು)</small>
                    </div>

                    <div class="form-group" id="compressionGroup" style="display: none;">
                        <label class="form-label" for="compressionSelect">ಸಂಕುಚನ ಮಟ್ಟ</label>
                        <select name="compression" id="compressionSelect" class="form-select" onchange="updateCompressionUI()">
                            <option value="low">ಕಡಿಮೆ (ಉತ್ತಮ ಗುಣಮಟ್ಟ)</option>
                            <option value="medium" selected>ಮಧ್ಯಮ</option>
                            <option value="high">ಹೆಚ್ಚು (ಚಿಕ್ಕ ಗಾತ್ರ)</option>
                            <option value="maximum">ಅತ್ಯಧಿಕ (ಅತಿ ಚಿಕ್ಕ ಗಾತ್ರ)</option>
                            <option value="custom">ಕಸ್ಟಮ್ ಗಾತ್ರ</option>
                        </select>
                    </div>

                    <div class="form-group" id="compareTypeGroup" style="display: none;">
                        <small>ಪಠ್ಯ ಹೋಲಿಕೆ ಕನ್ನಡ ಪಠ್ಯವನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ</small>
                    </div>

                    <div class="form-group" id="targetSizeGroup" style="display: none;">
                        <label class="form-label" for="targetSizeMB">ಗುರಿ ಫೈಲ್ ಗಾತ್ರ (MB ನಲ್ಲಿ)</label>
                        <input type="number" name="target_size_mb" id="targetSizeMB" class="form-input" placeholder="ಉದಾ: 2.5" step="0.1" min="0.1">
                        <small>ಮೂಲ ಫೈಲ್‌ಗಿಂತ ಚಿಕ್ಕ ಗಾತ್ರವನ್ನು ನಮೂದಿಸಿ</small>
                    </div>

                    <div class="form-group" id="advancedToggle" style="display: none;">
                        <label>
                            <input type="checkbox" id="showAdvancedComp" onchange="toggleAdvancedCompression()">
                            ಸುಧಾರಿತ ಆಯ್ಕೆಗಳನ್ನು ತೋರಿಸಿ
                        </label>
                    </div>

                    <div class="form-group" id="advancedCompressionOptions" style="display: none;">
                        <div class="advanced-grid">
                            <div>
                                <label class="form-label" for="imageQuality">ಚಿತ್ರ ಗುಣಮಟ್ಟ</label>
                                <input type="range" name="imageQuality" id="imageQuality" min="20" max="95" value="60" oninput="updateQualityDisplay()">
                                <span id="qualityValue">60%</span>
                            </div>
                            <div>
                                <label class="form-label" for="imageDPI">ರೆಸಲ್ಯೂಶನ್ (DPI)</label>
                                <select name="imageDPI" id="imageDPI" class="form-select">
                                    <option value="72">72 DPI (ಅತಿ ಸಣ್ಣ)</option>
                                    <option value="96">96 DPI (ಸಣ್ಣ)</option>
                                    <option value="150" selected>150 DPI (ಮಧ್ಯಮ)</option>
                                    <option value="200">200 DPI (ಉತ್ತಮ)</option>
                                    <option value="300">300 DPI (ಅತ್ಯುತ್ತಮ)</option>
                                </select>
                            </div>
                            <div>
                                <label>
                                    <input type="checkbox" name="removeMetadata" checked>
                                    ಮೆಟಾಡೇಟಾವನ್ನು ತೆಗೆದುಹಾಕಿ
                                </label>
                            </div>
                            <div>
                                <label>
                                    <input type="checkbox" name="optimizeFonts" checked>
                                    ಫಾಂಟ್‌ಗಳನ್ನು ಆಪ್ಟಿಮೈಜ್ ಮಾಡಿ
                                </label>
                            </div>
                        </div>
                    </div>

                    <div class="form-group" id="splitMethodGroup" style="display: none;">
                        <label class="form-label" for="splitMethodSelect">ವಿಭಾಗ ವಿಧಾನ</label>
                        <select name="split_method" id="splitMethodSelect" class="form-select" onchange="handleSplitMethodChange()">
                            <option value="pages">ನಿರ್ದಿಷ್ಟ ಪುಟಗಳು/ವ್ಯಾಪ್ತಿಗಳು</option>
                            <option value="size">ಗಾತ್ರದ ಆಧಾರದ ಮೇಲೆ</option>
                            <option value="auto">ಸ್ವಯಂಚಾಲಿತ ಚಂಕ್‌ಗಳು</option>
                        </select>
                    </div>

                    <div class="form-group" id="fileSizeGroup" style="display: none;">
                        <label class="form-label" for="maxSizeInput">ಪ್ರತಿ ಫೈಲ್ ಗರಿಷ್ಠ ಗಾತ್ರ (MB)</label>
                        <input type="number" name="target_size_mb" id="maxSizeInput" class="form-input" 
                            placeholder="10" min="1" max="50" value="10">
                        <small>ಪ್ರತಿ ಭಾಗದ ಅಂದಾಜು ಗಾತ್ರ</small>
                    </div>

                    <div class="form-group" id="autoChunkGroup" style="display: none;">
                        <label class="form-label" for="chunkSizeInput">ಪ್ರತಿ ಚಂಕ್‌ನಲ್ಲಿ ಪುಟಗಳು</label>
                        <input type="number" name="pages_per_chunk" id="chunkSizeInput" class="form-input" 
                            placeholder="20" min="5" max="100" value="20">
                        <small>ಪ್ರತಿ ಫೈಲ್‌ನಲ್ಲಿ ಎಷ್ಟು ಪುಟಗಳು</small>
                    </div>

                    <div class="form-group" id="rotationAngleGroup" style="display: none;">
                        <label class="form-label" for="rotationAngleSelect">ತಿರುಗುವ ಕೋನ</label>
                        <select name="rotation_angle" id="rotationAngleSelect" class="form-select">
                            <option value="90">90° (ಬಲಕ್ಕೆ)</option>
                            <option value="180">180° (ವಿಪರೀತ)</option>
                            <option value="270">270° (ಎಡಕ್ಕೆ)</option>
                            <option value="-90">-90° (ಎಡಕ್ಕೆ)</option>
                        </select>
                    </div>

                    <div class="form-group" id="applyToAllGroup" style="display: none;">
                        <label class="form-label">
                            <input type="checkbox" name="apply_to_all" id="applyToAllCheckbox" checked>
                            ಎಲ್ಲಾ ಪುಟಗಳಿಗೆ ಅನ್ವಯಿಸಿ
                        </label>
                        <small>ಇದನ್ನು ಆಫ್ ಮಾಡಿದರೆ ನಿರ್ದಿಷ್ಟ ಪುಟಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಬಹುದು</small>
                    </div>
                </div>

                <div class="form-group">
                    <button type="submit" class="btn btn-primary" id="processBtn" disabled>
                        <i class="fas fa-cog"></i> ಪ್ರಕ್ರಿಯೆ ಮಾಡಿ
                    </button>
                </div>
            </form>
        `;
        
        // Initialize UI components after DOM is created
        setTimeout(() => {
            if (config.options.includes('compression')) {
                updateCompressionUI();
                updateQualityDisplay();
            }
            if (config.options.includes('split_method')) {
                handleSplitMethodChange();
            }
            bindEventListeners();
        }, 50);
        
        console.log('=== MODAL CONTENT RESTORATION COMPLETE ===');
    }

    // CRITICAL FIX: Enhanced event listener binding
    function bindEventListeners() {
        console.log('=== BINDING EVENT LISTENERS ===');
        
        const uploadArea = safeGetElement('uploadArea');
        const fileInput = safeGetElement('fileInput');
        
        if (uploadArea && fileInput) {
            // Remove any existing event listeners by cloning elements
            const newUploadArea = uploadArea.cloneNode(true);
            const newFileInput = fileInput.cloneNode(true);
            
            uploadArea.parentNode.replaceChild(newUploadArea, uploadArea);
            fileInput.parentNode.replaceChild(newFileInput, fileInput);
            
            // Add fresh event listeners
            newUploadArea.onclick = () => newFileInput.click();
            
            newUploadArea.ondragover = (e) => {
                e.preventDefault();
                newUploadArea.classList.add('dragover');
            };
            
            newUploadArea.ondragleave = (e) => {
                e.preventDefault();
                newUploadArea.classList.remove('dragover');
            };
            
            newUploadArea.ondrop = (e) => {
                e.preventDefault();
                newUploadArea.classList.remove('dragover');
                const files = Array.from(e.dataTransfer.files);
                handleFileSelection(files);
            };
            
            newFileInput.onchange = (e) => {
                const files = Array.from(e.target.files);
                handleFileSelection(files);
            };
        }

        const form = safeGetElement('operationForm');
        if (form) {
            form.onsubmit = handleFormSubmission;
        }
        
        console.log('=== EVENT LISTENER BINDING COMPLETE ===');
    }

    async function handleFormSubmission(e) {
        e.preventDefault();
        
        const config = operationConfigs[currentOperation];
        if (selectedFiles.length < (config.minFiles || 1)) {
            if (currentOperation === 'merge') {
                showAlert('error', 'ವಿಲೀನಗೊಳಿಸಲು ಕನಿಷ್ಠ 2 PDF ಫೈಲ್‌ಗಳು ಬೇಕು');
            } else {
                showAlert('error', 'ದಯವಿಟ್ಟು ಕನಿಷ್ಠ ಒಂದು ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ');
            }
            return;
        }
        
        const formData = new FormData();
        formData.append('operation', currentOperation);
        
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        // Collect form data
        const selectedPagesInput = safeGetElement('selectedPagesInput');
        const pagesInput = safeGetElement('pagesInput');
        
        if (selectedPagesInput && selectedPagesInput.value) {
            formData.append('selected_pages', selectedPagesInput.value);
        } else if (pagesInput && pagesInput.value) {
            formData.append('pages', pagesInput.value);
        }
        
        // Add all other form parameters
        const compressionSelect = safeGetElement('compressionSelect');
        if (compressionSelect && compressionSelect.value) {
            formData.append('compression', compressionSelect.value);
        }

        const targetSizeMB = safeGetElement('targetSizeMB');
        if (targetSizeMB && targetSizeMB.value) {
            formData.append('target_size_mb', targetSizeMB.value);
        }

        const imageQuality = safeGetElement('imageQuality');
        if (imageQuality) {
            formData.append('imageQuality', imageQuality.value);
        }

        const imageDPI = safeGetElement('imageDPI');
        if (imageDPI) {
            formData.append('imageDPI', imageDPI.value);
        }

        const removeMetadata = document.querySelector('input[name="removeMetadata"]');
        if (removeMetadata) {
            formData.append('removeMetadata', removeMetadata.checked);
        }

        const optimizeFonts = document.querySelector('input[name="optimizeFonts"]');
        if (optimizeFonts) {
            formData.append('optimizeFonts', optimizeFonts.checked);
        }

        const splitMethodSelect = safeGetElement('splitMethodSelect');
        if (splitMethodSelect && splitMethodSelect.value) {
            formData.append('split_method', splitMethodSelect.value);
        }

        const maxSizeInput = safeGetElement('maxSizeInput');
        if (maxSizeInput && maxSizeInput.value) {
            formData.append('target_size_mb', maxSizeInput.value);
        }

        const chunkSizeInput = safeGetElement('chunkSizeInput');
        if (chunkSizeInput && chunkSizeInput.value) {
            formData.append('pages_per_chunk', chunkSizeInput.value);
        }
        
        const rotationAngleSelect = safeGetElement('rotationAngleSelect');
        if (rotationAngleSelect && rotationAngleSelect.value) {
            formData.append('rotation_angle', rotationAngleSelect.value);
        }
        
        const applyToAllCheckbox = safeGetElement('applyToAllCheckbox');
        if (applyToAllCheckbox) {
            formData.append('apply_to_all', applyToAllCheckbox.checked);
        }
        
        // Close operation modal and show loading
        const operationModal = safeGetElement('operationModal');
        const loadingModal = safeGetElement('loadingModal');
        
        if (operationModal) operationModal.style.display = 'none';
        if (loadingModal) loadingModal.style.display = 'block';
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Special handling for compare operation
                if (result.redirect_url) {
                    showAlert('success', result.message || 'ಕಾರ್ಯಾಚರಣೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!');
                    
                    setTimeout(() => {
                        window.location.href = result.redirect_url;
                    }, 1500);
                    
                    return;
                }
                
                // Regular operation success handling
                showSuccessModal(result);
                
                // CRITICAL FIX: Complete state reset after successful operation
                selectedFiles = [];
                selectedPages.clear();
                currentPreviewData = null;
            } else {
                showErrorModal(result.error);
            }
        } catch (error) {
            showErrorModal('ನೆಟ್‌ವರ್ಕ್ ದೋಷ: ' + error.message);
        } finally {
            if (loadingModal) loadingModal.style.display = 'none';
        }
    }

    function showSuccessModal(result) {
        const modal = safeGetElement('operationModal');
        if (!modal) return;
        
        const modalBody = modal.querySelector('.modal-body');
        if (!modalBody) return;
        
        modalBody.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; color: #4caf50; margin-bottom: 1rem;">✅</div>
                <h3>ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!</h3>
                <p style="margin: 1rem 0;">${result.message}</p>
                <div style="margin-top: 2rem;">
                    <a href="${result.download_url}" class="btn btn-primary" 
                       download="${result.filename}" style="margin-right: 1rem;">
                        <i class="fas fa-download"></i> ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ
                    </a>
                    <button class="btn" onclick="startNewOperation('${currentOperation}')" 
                            style="background: #6c757d; color: white; margin-right: 1rem;">
                        <i class="fas fa-redo"></i> ಮತ್ತೆ ${operationConfigs[currentOperation].title}
                    </button>
                    <button class="btn" onclick="closeModal()" style="background: #6c757d; color: white;">
                        ಮುಚ್ಚಿ
                    </button>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    function showErrorModal(errorMessage) {
        const modal = safeGetElement('operationModal');
        if (!modal) return;
        
        const modalBody = modal.querySelector('.modal-body');
        if (!modalBody) return;
        
        modalBody.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; color: #f44336; margin-bottom: 1rem;">❌</div>
                <h3>ದೋಷ ಸಂಭವಿಸಿದೆ</h3>
                <p style="margin: 1rem 0;">${errorMessage}</p>
                <div style="margin-top: 2rem;">
                    <button class="btn btn-primary" onclick="startNewOperation('${currentOperation}')">
                        <i class="fas fa-redo"></i> ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ
                    </button>
                    <button class="btn" onclick="closeModal()" style="background: #6c757d; color: white; margin-left: 1rem;">
                        ಮುಚ್ಚಿ
                    </button>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    // Utility functions
    function parsePageRanges(pagesStr, totalPages) {
        const pages = [];
        const parts = pagesStr.split(',');

        for (let part of parts) {
            part = part.trim();
            if (part.includes('-')) {
                const [start, end] = part.split('-').map(x => parseInt(x.trim()));
                if (isNaN(start) || isNaN(end) || start > end) {
                    throw new Error(`ಅಮಾನ್ಯ ವ್ಯಾಪ್ತಿ: ${part}`);
                }
                for (let i = start; i <= Math.min(end, totalPages); i++) {
                    if (i >= 1) pages.push(i);
                }
            } else {
                const pageNum = parseInt(part);
                if (isNaN(pageNum) || pageNum < 1 || pageNum > totalPages) {
                    throw new Error(`ಅಮಾನ್ಯ ಪುಟ ಸಂಖ್ಯೆ: ${part}`);
                }
                pages.push(pageNum);
            }
        }

        return [...new Set(pages)].sort((a, b) => a - b);
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

    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            ${message}
        `;
        
        // Add to modal body or create container
        const modalBody = document.querySelector('#operationModal .modal-body');
        if (modalBody) {
            modalBody.insertBefore(alertDiv, modalBody.firstChild);
        }
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
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

    // Compare operation specific handlers
    const operationCards = document.querySelectorAll('.operation-card');
    
    operationCards.forEach(card => {
        card.addEventListener('click', function() {
            const operation = this.dataset.operation;
            
            if (operation === 'compare') {
                // Show special message for compare
                const uploadText = document.querySelector('.upload-text');
                if (uploadText) {
                    uploadText.innerHTML = 
                        '<i class="fas fa-balance-scale"></i> ಹೋಲಿಕೆಗಾಗಿ 2 PDF ಫೈಲ್‌ಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ';
                }
                
                // Set file input to accept multiple files
                const fileInput = document.querySelector('input[type="file"]');
                if (fileInput) {
                    fileInput.multiple = true;
                    fileInput.accept = '.pdf';
                }
            }
        });
    });
    
    // Add validation before form submission
    const uploadForm = document.querySelector('#uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const operation = document.querySelector('input[name="operation"]')?.value;
            
            if (operation === 'compare') {
                if (!validateCompareOperation()) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }
});