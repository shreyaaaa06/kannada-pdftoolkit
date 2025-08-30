document.addEventListener('DOMContentLoaded', function() {

    // Function to show menu content modal
    window.showMenuContent = function(menuKey) {
        const modal = safeGetElement('operationModal');
        if (!modal) return;
        const modalBody = modal.querySelector('.modal-body');
        if (!modalBody) return;
        const info = menuContents[menuKey];
        if (!info) return;
        modalBody.innerHTML = `<h2 style="text-align:center; color:#5d4037;">${info.title}</h2><div style="margin:2rem 0; font-size:1.1rem; color:#3e2723; text-align:center;">${info.content}</div><div style="text-align:center;"><button class='btn btn-primary' onclick='closeModal()'>ಮುಚ್ಚಿ</button></div>`;
        modal.style.display = 'block';
    };
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
        },
         'sort': {
            title: 'PDF ಪುಟಗಳನ್ನು ಸಂಖ್ಯೆ ಆಧಾರಿತವಾಗಿ ಸಾರಿ ಹಾಕಿ',
            accept: '.pdf',
            supportText: 'ಒಂದು PDF ಫೈಲ್ ಮಾತ್ರ',
            multiple: false,
            options: ['pages'], // Enable manual selection
            minFiles: 1,
            hasPreview: true
        },
            
            'protect': {
                title: 'PDF ರಕ್ಷಿಸಿ',
                accept: '.pdf',
                supportText: 'ಒಂದು PDF ಫೈಲ್ ಮಾತ್ರ - ಪಾಸ್‌ವರ್ಡ್‌ನೊಂದಿಗೆ ಎನ್‌ಕ್ರಿಪ್ಟ್ ಮಾಡಿ',
                multiple: false,
                options: ['protect'],
                minFiles: 1,
                hasPreview: false
            },
            'unlock': {
                title: 'PDF ಅನ್‌ಲಾಕ್ ಮಾಡಿ',
                accept: '.pdf',
                supportText: 'ಒಂದು PDF ಫೈಲ್ ಮಾತ್ರ - ಪಾಸ್‌ವರ್ಡ್ ರಕ್ಷಿತ PDF ಅನ್‌ಲಾಕ್ ಮಾಡಿ',
                multiple: false,
                options: ['unlock'],
                minFiles: 1,
                hasPreview: false
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
    }

    window.showSortPreview = async function() {
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
            const response = await fetch('/generate-sort-preview', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.success) {
                currentPreviewData = result;
                displaySortPreview(result);
            } else {
                throw new Error(result.error || 'ಸಾರಿಸುವ ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ');
            }
        } catch (error) {
            showAlert('error', 'ಸಾರಿಸುವ ಪೂರ್ವವೀಕ್ಷಣೆ ಲೋಡ್ ಮಾಡಲಾಗಲಿಲ್ಲ: ' + error.message);
            closePreviewModal();
        } finally {
            loadingPreview.style.display = 'none';
        }
    }

    function displaySortPreview(previewData) {
        const pagesGrid = document.getElementById('pagesGrid');
        pagesGrid.innerHTML = '';
        // Create main content area with full width sorted preview
        const mainContent = document.createElement('div');
        mainContent.style.cssText = `
            display: flex;
            height: 75vh;
            width: 150vh;
            min-height: 600px;
            max-height: 800px;
            justify-content: center;
        `;
        // Full width - Sorted preview with checkboxes
        const sortedOrderDiv = document.createElement('div');
        sortedOrderDiv.className = 'sorted-order-preview';
        sortedOrderDiv.style.cssText = `
            background: var(--white);
            padding: 1rem;
            width: 100%;
            flex: 1;
            border-radius: 8px;
            border: 1px solid var(--light-brown);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        `;
        if (previewData.sorted_order && previewData.sorted_order.length > 0) {
            sortedOrderDiv.innerHTML = `
                <h5 style="color: var(--brown-text); margin-bottom: 0.5rem;">
                    <i class="fas fa-check-square"></i> ಸಾರಿಸಿದ ಪುಟಗಳ ಪೂರ್ವವೀಕ್ಷಣೆ - ಆಯ್ಕೆ ಮಾಡಿ:
                    ${previewData.total_pages > 500 ? `<span style="font-size: 0.7rem; color: var(--light-brown);"> (ಮೊದಲ 500 ಪುಟಗಳು - ಒಟ್ಟು ${previewData.total_pages})</span>` : ''}
                </h5>
                <p style="color: var(--light-brown); font-size: 0.8rem; margin-bottom: 0.8rem; background: var(--biscuit-light); padding: 0.5rem; border-radius: 4px;">
                    ✅ ಚೆಕ್‌ಬಾಕ್ಸ್ ಕ್ಲಿಕ್ ಮಾಡಿ ಅಥವಾ ಪುಟವನ್ನು ಟ್ಯಾಪ್ ಮಾಡಿ ಆಯ್ಕೆ ಮಾಡಲು
                </p>
                <div style="flex: 1; overflow-y: auto; padding: 0.8rem; border: 1px solid var(--biscuit-light); border-radius: 8px; background: var(--biscuit-light);">
                    <div style="display: flex; flex-wrap: wrap; gap: 1rem; justify-content: flex-start;">
                        ${previewData.sorted_order.map((page, index) => `
                            <div class="sorted-page-item" data-page-num="${page.page_num}" style="text-align: center; background: var(--biscuit-cream); border-radius: 8px; padding: 0.8rem; min-width: 140px; cursor: pointer; position: relative;">
                                <input type="checkbox" class="sorted-page-checkbox" onchange="togglePageSelection(${page.page_num})" 
                                       style="position: absolute; top: 8px; left: 8px; transform: scale(1.3);">
                                <div style="color: var(--brown-text); font-weight: bold; margin-bottom: 0.5rem; font-size: 0.85rem; margin-top: 20px;">
                                    ${index + 1}. ಪುಟ ${page.page_num}
                                </div>
                                ${page.thumbnail_path ? `
                                    <img src="${page.thumbnail_path}" alt="ಪುಟ ${page.page_num}" 
                                         style="width: 90px; height: 120px; border: 1px solid var(--light-brown); border-radius: 4px; object-fit: cover; margin-bottom: 0.5rem;"
                                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                    <div style="display: none; width: 90px; height: 120px; background: var(--biscuit-light); border: 1px solid var(--light-brown); border-radius: 4px; align-items: center; justify-content: center; color: var(--light-brown); font-size: 0.75rem; margin-bottom: 0.5rem;">
                                        📄<br><span style="font-size: 0.65rem;">ಪುಟ ${page.page_num}</span>
                                    </div>
                                ` : `
                                    <div style="width: 90px; height: 120px; background: var(--biscuit-light); border: 1px solid var(--light-brown); border-radius: 4px; display: flex; align-items: center; justify-content: center; color: var(--light-brown); font-size: 0.75rem; margin-bottom: 0.5rem; flex-direction: column;">
                                        <div>📄</div>
                                        <div style="font-size: 0.65rem;">ಪುಟ ${page.page_num}</div>
                                    </div>
                                `}
                                <div style="color: var(--light-brown); font-size: 0.7rem;">
                                    ಸಂಖ್ಯೆ: ${page.extracted_number}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
         mainContent.appendChild(sortedOrderDiv);
            pagesGrid.appendChild(mainContent);

            // Add click event listeners for sorted page selection
            if (sortedOrderDiv.querySelectorAll) {
                sortedOrderDiv.querySelectorAll('.sorted-page-item').forEach(pageDiv => {
                    pageDiv.onclick = (e) => {
                        if (e.target.type !== 'checkbox') {
                            const pageNum = parseInt(pageDiv.dataset.pageNum);
                            togglePageSelection(pageNum);
                            const checkbox = pageDiv.querySelector('.sorted-page-checkbox');
                            checkbox.checked = selectedPages.has(pageNum);
                        }
                    };
                });
            }

            // Select all pages by default for sorting and update checkboxes
            previewData.previews.forEach(preview => {
                selectedPages.add(preview.page_num);
                
                // Update sorted preview checkboxes
                const sortedPageDiv = sortedOrderDiv.querySelector(`[data-page-num="${preview.page_num}"]`);
                if (sortedPageDiv) {
                    const checkbox = sortedPageDiv.querySelector('.sorted-page-checkbox');
                    if (checkbox) {
                        checkbox.checked = true;
                    }
                    sortedPageDiv.style.borderColor = 'var(--gold)';
                    sortedPageDiv.style.background = 'var(--biscuit-light)';
                }
            });

            updateSelectedPagesDisplay();
        }
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
         if (previewSection && config.hasPreview && selectedFiles.length > 0) {
                previewSection.style.display = 'block';
            } else if (previewSection) {
                previewSection.style.display = 'none';
            }
        }

        async function showPagePreview() {
            if (selectedFiles.length === 0) {
                showAlert('error', 'ದಯವಿಟ್ಟು ಮೊದಲು PDF ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ');
                return;
            }

            // Check if this is a sort operation
            if (currentOperation === 'sort') {
                await showSortPreview();
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

                const result = await response.json();

                if (result.success) {
                    currentPreviewData = result;
                    displayPagePreviews(result);
                } else {
                    throw new Error(result.error || 'ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ');
                }
            } catch (error) {
                showAlert('error', 'ಪೂರ್ವವೀಕ್ಷಣೆ ಲೋಡ್ ಮಾಡಲಾಗಲಿಲ್ಲ: ' + error.message);
                closePreviewModal();
            } finally {
                loadingPreview.style.display = 'none';
            }
        }

    // Replace your showOperationOptions function with this fixed version:

    function showOperationOptions(options, hasPreview) {
    const optionGroups = ['pagesGroup', 'compressionGroup', 'compareTypeGroup', 'splitMethodGroup', 
                         'fileSizeGroup', 'autoChunkGroup', 'rotationAngleGroup', 'applyToAllGroup'];
    
    // Hide all option groups first
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
                // Map the option names to their corresponding group IDs
                let groupId;
                switch(option) {
                    case 'split_method':
                        groupId = 'splitMethodGroup';
                        break;
                    case 'pages':
                        groupId = 'pagesGroup';
                        break;
                    case 'compression':
                        groupId = 'compressionGroup';
                        break;
                    case 'compareType':
                        groupId = 'compareTypeGroup';
                        break;
                    case 'rotation_angle':
                        groupId = 'rotationAngleGroup';
                        break;
                    case 'apply_to_all':
                        groupId = 'applyToAllGroup';
                        break;
                    default:
                        groupId = option + 'Group';
                }
                const element = safeGetElement(groupId);
                if (element) {
                    element.style.display = 'block';
                    // Special handling for split method to trigger the change handler
                    if (option === 'split_method') {
                        setTimeout(() => handleSplitMethodChange(), 100);
                    }
                }
            });
            // Toggle required attribute for password fields based on operation
            // Protect PDF
            const protectGroup = safeGetElement('protectGroup');
            const protectionPassword = safeGetElement('protectionPassword');
            const confirmPassword = safeGetElement('confirmPassword');
            if (protectGroup && protectionPassword && confirmPassword) {
                if (protectGroup.style.display === 'block') {
                    protectionPassword.required = true;
                    confirmPassword.required = true;
                } else {
                    protectionPassword.required = false;
                    confirmPassword.required = false;
                }
            }
            // Unlock PDF
            const unlockGroup = safeGetElement('unlockGroup');
            const unlockPassword = safeGetElement('unlockPassword');
            if (unlockGroup && unlockPassword) {
                if (unlockGroup.style.display === 'block') {
                    unlockPassword.required = true;
                } else {
                    unlockPassword.required = false;
                }
            }
        } else {
            operationOptions.style.display = 'none';
            // Remove required from all password fields if no options
            const protectionPassword = safeGetElement('protectionPassword');
            const confirmPassword = safeGetElement('confirmPassword');
            const unlockPassword = safeGetElement('unlockPassword');
            if (protectionPassword) protectionPassword.required = false;
            if (confirmPassword) confirmPassword.required = false;
            if (unlockPassword) unlockPassword.required = false;
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
                    
                    
                    <div class="form-group" id="protectGroup" style="display: ${config.options && config.options.includes('protect') ? 'block' : 'none'};">
                        <h4 style="color: var(--brown-text); margin-bottom: 1rem;">
                            <i class="fas fa-lock"></i> PDF ರಕ್ಷಣೆ ಸೆಟ್ಟಿಂಗ್ಸ್
                        </h4>
                        
                        <!-- Password Input -->
                        <div class="form-group">
                            <label class="form-label" for="protectionPassword">
                                <i class="fas fa-key"></i> ಪಾಸ್‌ವರ್ಡ್ ಸೆಟ್ ಮಾಡಿ
                            </label>
                            <input type="password" name="protection_password" id="protectionPassword" 
                                   class="form-input" placeholder="ಸುರಕ್ಷಿತ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ" required>
                            <small style="color: var(--light-brown);">
                                <i class="fas fa-info-circle"></i> 
                                ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು, ಅಕ್ಷರ ಮತ್ತು ಸಂಖ್ಯೆಗಳ ಸಂಯೋಜನೆ ಶಿಫಾರಸು
                            </small>
                        </div>

                        <!-- Confirm Password -->
                        <div class="form-group">
                            <label class="form-label" for="confirmPassword">
                                <i class="fas fa-key"></i> ಪಾಸ್‌ವರ್ಡ್ ಖಚಿತಪಡಿಸಿ
                            </label>
                            <input type="password" name="confirm_password" id="confirmPassword" 
                                   class="form-input" placeholder="ಪಾಸ್‌ವರ್ಡ್ ಮತ್ತೆ ನಮೂದಿಸಿ" required>
                        </div>

                        <!-- Protection Level -->
                        <div class="form-group">
                            <label class="form-label" for="protectionLevel">
                                <i class="fas fa-shield-alt"></i> ಸುರಕ್ಷತೆ ಮಟ್ಟ
                            </label>
                            <select name="protection_level" id="protectionLevel" class="form-select">
                                <option value="128" selected>ಮಧ್ಯಮ ಸುರಕ್ಷತೆ (128-bit)</option>
                                <option value="256">ಹೆಚ್ಚು ಸುರಕ್ಷತೆ (256-bit)</option>
                            </select>
                        </div>

                        <!-- Permission Settings -->
                        <details style="margin-top: 1rem; border: 1px solid var(--biscuit-light); border-radius: 8px; padding: 1rem;">
                            <summary style="cursor: pointer; font-weight: 600; color: var(--brown-text);">
                                <i class="fas fa-cog"></i> ಅನುಮತಿ ಸೆಟ್ಟಿಂಗ್ಸ್ (ಐಚ್ಛಿಕ)
                            </summary>
                            <div style="margin-top: 1rem;">
                                <div style="display: grid; gap: 0.8rem;">
                                    <label style="display: flex; align-items: center; gap: 0.5rem;">
                                        <input type="checkbox" name="allow_printing" value="true" checked>
                                        <i class="fas fa-print"></i> ಮುದ್ರಣ ಅನುಮತಿಸಿ
                                    </label>
                                    <label style="display: flex; align-items: center; gap: 0.5rem;">
                                        <input type="checkbox" name="allow_copying" value="true">
                                        <i class="fas fa-copy"></i> ಪಠ್ಯ ನಕಲು ಅನುಮತಿಸಿ
                                    </label>
                                    <label style="display: flex; align-items: center; gap: 0.5rem;">
                                        <input type="checkbox" name="allow_modification" value="true">
                                        <i class="fas fa-edit"></i> ಸಂಪಾದನೆ ಅನುಮತಿಸಿ
                                    </label>
                                    <label style="display: flex; align-items: center; gap: 0.5rem;">
                                        <input type="checkbox" name="allow_annotation" value="true" checked>
                                        <i class="fas fa-comment"></i> ಟಿಪ್ಪಣಿಗಳು ಅನುಮತಿಸಿ
                                    </label>
                                    <label style="display: flex; align-items: center; gap: 0.5rem;">
                                        <input type="checkbox" name="allow_form_filling" value="true" checked>
                                        <i class="fas fa-wpforms"></i> ಫಾರ್ಮ್ ಭರ್ತಿ ಅನುಮತಿಸಿ
                                    </label>
                                </div>
                            </div>
                        </details>

                        <!-- Security Notice -->
                        <div style="background: rgba(30, 58, 138, 0.1); border: 1px solid var(--gov-blue); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                            <p style="margin: 0; color: var(--gov-blue); font-size: 0.9rem;">
                                <i class="fas fa-info-circle"></i>
                                <strong>ಸೂಚನೆ:</strong> ಪಾಸ್‌ವರ್ಡ್ ಅನ್ನು ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ಇರಿಸಿ. ಕಳೆದುಹೋದ ಪಾಸ್‌ವರ್ಡ್ ಅನ್ನು ಮರುಪ್ರಾಪ್ತಿ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ.
                            </p>
                        </div>
                    </div>

                    <div class="form-group" id="unlockGroup" style="display: ${config.options && config.options.includes('unlock') ? 'block' : 'none'};">
                        <h4 style="color: var(--brown-text); margin-bottom: 1rem;">
                            <i class="fas fa-unlock"></i> PDF ಅನ್‌ಲಾಕ್ ಸೆಟ್ಟಿಂಗ್ಸ್
                        </h4>
                        
                        <!-- Unlock Password Input -->
                        <div class="form-group">
                            <label class="form-label" for="unlockPassword">
                                <i class="fas fa-key"></i> PDF ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ
                            </label>
                            <input type="password" name="unlock_password" id="unlockPassword" 
                                   class="form-input" placeholder="ರಕ್ಷಿತ PDF ಅನ್‌ಲಾಕ್ ಮಾಡಲು ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ" required>
                            <small style="color: var(--light-brown);">
                                <i class="fas fa-info-circle"></i> 
                                ಈ PDF ಫೈಲ್ ಅನ್ನು ರಕ್ಷಿಸಲು ಬಳಸಿದ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ
                            </small>
                        </div>

                        <!-- Unlock Notice -->
                        <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid var(--success-green); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                            <p style="margin: 0; color: var(--success-green); font-size: 0.9rem;">
                                <i class="fas fa-shield-alt"></i>
                                <strong>ಸೂಚನೆ:</strong> ಯಶಸ್ವಿಯಾದ ನಂತರ, ನೀವು ಪಾಸ್‌ವರ್ಡ್ ರಹಿತ PDF ಫೈಲ್ ಪಡೆಯುತ್ತೀರಿ ಅದನ್ನು ಯಾರಾದರೂ ತೆರೆಯಬಹುದು.
                            </p>
                        </div>
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
        // Add password fields for protect and unlock before fetch
        if (currentOperation === 'protect') {
            const protectionPassword = document.getElementById('protectionPassword');
            if (protectionPassword && protectionPassword.value) {
                formData.append('protection_password', protectionPassword.value);
            }
            const confirmPassword = document.getElementById('confirmPassword');
            if (confirmPassword && confirmPassword.value) {
                formData.append('confirm_password', confirmPassword.value);
            }
            const protectionLevel = document.getElementById('protectionLevel');
            if (protectionLevel && protectionLevel.value) {
                formData.append('protection_level', protectionLevel.value);
            }
            // Permission checkboxes
            const allowPrinting = document.querySelector('input[name="allow_printing"]:checked');
            if (allowPrinting) formData.append('allow_printing', 'true');
            const allowCopying = document.querySelector('input[name="allow_copying"]:checked');
            if (allowCopying) formData.append('allow_copying', 'true');
            const allowModification = document.querySelector('input[name="allow_modification"]:checked');
            if (allowModification) formData.append('allow_modification', 'true');
            const allowAnnotation = document.querySelector('input[name="allow_annotation"]:checked');
            if (allowAnnotation) formData.append('allow_annotation', 'true');
            const allowFormFilling = document.querySelector('input[name="allow_form_filling"]:checked');
            if (allowFormFilling) formData.append('allow_form_filling', 'true');
        }
        if (currentOperation === 'unlock') {
            const unlockPassword = document.getElementById('unlockPassword');
            if (unlockPassword && unlockPassword.value) {
                formData.append('unlock_password', unlockPassword.value);
            }
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
            // Handle result after fetch
            if (result.success) {
                // Special handling for compare operation
                if (result.redirect_url) {
                    showAlert('success', result.message || 'ಕಾರ್ಯಾಚರಣೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!');
                    setTimeout(() => {
                        window.location.href = result.redirect_url;
                    }, 1500);
                    return;
                }
                showSuccessModal(result);
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

    async function showSortPreview() {
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

                const response = await fetch('/generate-sort-preview', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    currentPreviewData = result;
                    displaySortPreview(result);
                } else {
                    throw new Error(result.error || 'ಸಾರಿಸುವ ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ');
                }
            } catch (error) {
                showAlert('error', 'ಸಾರಿಸುವ ಪೂರ್ವವೀಕ್ಷಣೆ ಲೋಡ್ ಮಾಡಲಾಗಲಿಲ್ಲ: ' + error.message);
                closePreviewModal();
            } finally {
                loadingPreview.style.display = 'none';
            }
        }

        function displaySortPreview(previewData) {
            const pagesGrid = document.getElementById('pagesGrid');
            pagesGrid.innerHTML = '';

            // Create main content area with full width sorted preview
            const mainContent = document.createElement('div');
            mainContent.style.cssText = `
                display: flex;
                height: 75vh;
                width: 150vh;
                min-height: 600px;
                max-height: 800px;
                justify-content: center;
            `;

            // Full width - Sorted preview with checkboxes
            const sortedOrderDiv = document.createElement('div');
            sortedOrderDiv.className = 'sorted-order-preview';
            sortedOrderDiv.style.cssText = `
                background: var(--white);
                padding: 1rem;
                width: 100%;
                flex: 1;
                border-radius: 8px;
                border: 1px solid var(--light-brown);
                overflow: hidden;
                display: flex;
                flex-direction: column;
            `;
            if (previewData.sorted_order && previewData.sorted_order.length > 0) {
                sortedOrderDiv.innerHTML = `
                    <h5 style="color: var(--brown-text); margin-bottom: 0.5rem;">
                        <i class="fas fa-check-square"></i> ಸಾರಿಸಿದ ಪುಟಗಳ ಪೂರ್ವವೀಕ್ಷಣೆ - ಆಯ್ಕೆ ಮಾಡಿ:
                        ${previewData.total_pages > 500 ? `<span style="font-size: 0.7rem; color: var(--light-brown);"> (ಮೊದಲ 500 ಪುಟಗಳು - ಒಟ್ಟು ${previewData.total_pages})</span>` : ''}
                    </h5>
                    <p style="color: var(--light-brown); font-size: 0.8rem; margin-bottom: 0.8rem; background: var(--biscuit-light); padding: 0.5rem; border-radius: 4px;">
                        ✅ ಚೆಕ್‌ಬಾಕ್ಸ್ ಕ್ಲಿಕ್ ಮಾಡಿ ಅಥವಾ ಪುಟವನ್ನು ಟ್ಯಾಪ್ ಮಾಡಿ ಆಯ್ಕೆ ಮಾಡಲು
                    </p>
                    <div style="flex: 1; overflow-y: auto; padding: 0.8rem; border: 1px solid var(--biscuit-light); border-radius: 8px; background: var(--biscuit-light);">
                        <div style="display: flex; flex-wrap: wrap; gap: 1rem; justify-content: flex-start;">
                            ${previewData.sorted_order.map((page, index) => `
                                <div class="sorted-page-item" data-page-num="${page.page_num}" style="text-align: center; background: var(--biscuit-cream); border-radius: 8px; padding: 0.8rem; min-width: 140px; cursor: pointer; position: relative;">
                                    <input type="checkbox" class="sorted-page-checkbox" onchange="togglePageSelection(${page.page_num})" 
                                           style="position: absolute; top: 8px; left: 8px; transform: scale(1.3);">
                                    <div style="color: var(--brown-text); font-weight: bold; margin-bottom: 0.5rem; font-size: 0.85rem; margin-top: 20px;">
                                        ${index + 1}. ಪುಟ ${page.page_num}
                                    </div>
                                    ${page.thumbnail_path ? `
                                        <img src="${page.thumbnail_path}" alt="ಪುಟ ${page.page_num}" 
                                             style="width: 90px; height: 120px; border: 1px solid var(--light-brown); border-radius: 4px; object-fit: cover; margin-bottom: 0.5rem;"
                                             onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                        <div style="display: none; width: 90px; height: 120px; background: var(--biscuit-light); border: 1px solid var(--light-brown); border-radius: 4px; align-items: center; justify-content: center; color: var(--light-brown); font-size: 0.75rem; margin-bottom: 0.5rem;">
                                            📄<br><span style="font-size: 0.65rem;">ಪುಟ ${page.page_num}</span>
                                        </div>
                                    ` : `
                                        <div style="width: 90px; height: 120px; background: var(--biscuit-light); border: 1px solid var(--light-brown); border-radius: 4px; display: flex; align-items: center; justify-content: center; color: var(--light-brown); font-size: 0.75rem; margin-bottom: 0.5rem; flex-direction: column;">
                                            <div>📄</div>
                                            <div style="font-size: 0.65rem;">ಪುಟ ${page.page_num}</div>
                                        </div>
                                    `}
                                    <div style="color: var(--light-brown); font-size: 0.7rem;">
                                        ಸಂಖ್ಯೆ: ${page.extracted_number}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }


            // Add only the sorted preview to main content
            mainContent.appendChild(sortedOrderDiv);
            pagesGrid.appendChild(mainContent);

            // Add click event listeners for sorted page selection
            if (sortedOrderDiv.querySelectorAll) {
                sortedOrderDiv.querySelectorAll('.sorted-page-item').forEach(pageDiv => {
                    pageDiv.onclick = (e) => {
                        if (e.target.type !== 'checkbox') {
                            const pageNum = parseInt(pageDiv.dataset.pageNum);
                            togglePageSelection(pageNum);
                            const checkbox = pageDiv.querySelector('.sorted-page-checkbox');
                            checkbox.checked = selectedPages.has(pageNum);
                        }
                    };
                });
            }

            // Select all pages by default for sorting and update checkboxes
            previewData.previews.forEach(preview => {
                selectedPages.add(preview.page_num);
                
                // Update sorted preview checkboxes
                const sortedPageDiv = sortedOrderDiv.querySelector(`[data-page-num="${preview.page_num}"]`);
                if (sortedPageDiv) {
                    const checkbox = sortedPageDiv.querySelector('.sorted-page-checkbox');
                    if (checkbox) {
                        checkbox.checked = true;
                    }
                    sortedPageDiv.style.borderColor = 'var(--gold)';
                    sortedPageDiv.style.background = 'var(--biscuit-light)';
                }
            });

            updateSelectedPagesDisplay();
        }
        // Language change function
        function changeLanguage(lang, langName, flagClass, event) {
            // Prevent default link behavior
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Store language preference
            localStorage.setItem('preferredLanguage', lang);
            localStorage.setItem('preferredLanguageName', langName);
            localStorage.setItem('preferredLanguageFlag', flagClass);
            
            // Update current language display
            const currentLang = document.getElementById('currentLanguage');
            const currentFlag = document.querySelector('.language-button .language-flag');
            
            if (currentLang) currentLang.textContent = langName;
            if (currentFlag) {
                currentFlag.className = `language-flag ${flagClass}`;
            }
            
            // Update active state
            document.querySelectorAll('.language-option').forEach(option => {
                option.classList.remove('active');
            });
            
            // Add active class to clicked option
            if (event && event.target) {
                const clickedOption = event.target.closest('.language-option');
                if (clickedOption) {
                    clickedOption.classList.add('active');
                }
            }
            
            // Close dropdown
            const dropdown = document.getElementById('languageDropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }
            
            console.log('Language changed to:', lang, langName);
            
            // Show notification based on language
            if (lang === 'en') {
                showLanguageNotification('English language support will be added soon!', 'info');
            } else {
                showLanguageNotification('ಭಾಷೆ ಬದಲಾಯಿಸಲಾಗಿದೆ: ' + langName, 'success');
            }
        }

        function showLanguageNotification(message, type) {
            // Create notification element
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${type === 'success' ? 'var(--success-green)' : 'var(--gov-blue)'};
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                z-index: 10000;
                font-family: 'Noto Sans Kannada', sans-serif;
                font-size: 0.9rem;
                max-width: 300px;
                animation: slideInRight 0.3s ease;
            `;
            notification.textContent = message;
            
            // Add animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
            
            // Show notification
            document.body.appendChild(notification);
            
            // Remove after 3 seconds
            setTimeout(() => {
                notification.style.animation = 'slideInRight 0.3s ease reverse';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                    if (style.parentNode) {
                        style.parentNode.removeChild(style);
                    }
                }, 300);
            }, 3000);
        }

        // Load preferred language on page load
        document.addEventListener('DOMContentLoaded', function() {
            const preferredLang = localStorage.getItem('preferredLanguage') || 'kn';
            const preferredLangName = localStorage.getItem('preferredLanguageName') || 'ಕನ್ನಡ';
            const preferredLangFlag = localStorage.getItem('preferredLanguageFlag') || 'flag-kn';
            
            // Set initial language display
            const currentLang = document.getElementById('currentLanguage');
            const currentFlag = document.querySelector('.language-button .language-flag');
            
            if (currentLang) currentLang.textContent = preferredLangName;
            if (currentFlag) {
                currentFlag.className = `language-flag ${preferredLangFlag}`;
            }
            
            // Update active state
            document.querySelectorAll('.language-option').forEach(option => {
                option.classList.remove('active');
                const optionLang = option.getAttribute('onclick').match(/'(\w+)'/)[1];
                if (optionLang === preferredLang) {
                    option.classList.add('active');
                }
            });
        });

        // Password validation for PDF protection
        function initializePasswordValidation() {
            const protectionPassword = document.getElementById('protectionPassword');
            const confirmPassword = document.getElementById('confirmPassword');
            
            if (protectionPassword && confirmPassword) {
                protectionPassword.addEventListener('input', validatePassword);
                confirmPassword.addEventListener('input', validatePasswordMatch);
            }
        }

        function validatePassword() {
            const password = document.getElementById('protectionPassword').value;
            const feedback = document.getElementById('passwordFeedback');
            
            // Remove existing feedback
            if (feedback) feedback.remove();
            
            const requirements = {
                length: password.length >= 6,
                hasLetter: /[a-zA-Z]/.test(password),
                hasNumber: /[0-9]/.test(password),
                noSpaces: !/\s/.test(password)
            };
            
            const isValid = Object.values(requirements).every(req => req);
            const input = document.getElementById('protectionPassword');
            
            // Create feedback element
            const feedbackDiv = document.createElement('div');
            feedbackDiv.id = 'passwordFeedback';
            feedbackDiv.style.marginTop = '0.5rem';
            feedbackDiv.style.fontSize = '0.85rem';
            
            if (password.length === 0) {
                input.style.borderColor = '';
                return;
            }
            
            if (isValid) {
                input.style.borderColor = '#28a745';
                feedbackDiv.innerHTML = `
                    <div style="color: #28a745;">
                        <i class="fas fa-check-circle"></i> ಪಾಸ್‌ವರ್ಡ್ ಬಲವಾಗಿದೆ
                    </div>
                `;
            } else {
                input.style.borderColor = '#dc3545';
                feedbackDiv.innerHTML = `
                    <div style="color: #dc3545;">
                        <i class="fas fa-exclamation-triangle"></i> ಪಾಸ್‌ವರ್ಡ್ ಅವಶ್ಯಕತೆಗಳು:
                        <ul style="margin: 0.3rem 0 0 1rem; font-size: 0.8rem;">
                            <li style="color: ${requirements.length ? '#28a745' : '#dc3545'}">
                                ${requirements.length ? '✓' : '✗'} ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು
                            </li>
                            <li style="color: ${requirements.hasLetter ? '#28a745' : '#dc3545'}">
                                ${requirements.hasLetter ? '✓' : '✗'} ಕನಿಷ್ಠ ಒಂದು ಅಕ್ಷರ
                            </li>
                            <li style="color: ${requirements.hasNumber ? '#28a745' : '#dc3545'}">
                                ${requirements.hasNumber ? '✓' : '✗'} ಕನಿಷ್ಠ ಒಂದು ಸಂಖ್ಯೆ
                            </li>
                            <li style="color: ${requirements.noSpaces ? '#28a745' : '#dc3545'}">
                                ${requirements.noSpaces ? '✓' : '✗'} ಸ್ಪೇಸ್‌ಗಳಿಲ್ಲ
                            </li>
                        </ul>
                    </div>
                `;
            }
            
            input.parentNode.appendChild(feedbackDiv);
            
            // Re-validate password match
            validatePasswordMatch();
        }

        function validatePasswordMatch() {
            const password = document.getElementById('protectionPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const input = document.getElementById('confirmPassword');
            const feedback = document.getElementById('confirmPasswordFeedback');
            
            // Remove existing feedback
            if (feedback) feedback.remove();
            
            if (confirmPassword.length === 0) {
                input.style.borderColor = '';
                return;
            }
            
            const feedbackDiv = document.createElement('div');
            feedbackDiv.id = 'confirmPasswordFeedback';
            feedbackDiv.style.marginTop = '0.5rem';
            feedbackDiv.style.fontSize = '0.85rem';
            
            if (password === confirmPassword) {
                input.style.borderColor = '#28a745';
                feedbackDiv.innerHTML = `
                    <div style="color: #28a745;">
                        <i class="fas fa-check-circle"></i> ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತವೆ
                    </div>
                `;
            } else {
                input.style.borderColor = '#dc3545';
                feedbackDiv.innerHTML = `
                    <div style="color: #dc3545;">
                        <i class="fas fa-times-circle"></i> ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ
                    </div>
                `;
            }
            
            input.parentNode.appendChild(feedbackDiv);
        }
        document.addEventListener('DOMContentLoaded', function() {
            // Add click handlers for menu items
            const menuLinks = document.querySelectorAll('.menu-item a, .dropdown-item');
            menuLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    const href = this.getAttribute('href');
                    if (href && href.startsWith('#')) {
                        e.preventDefault();
                        const sectionId = href.substring(1);
                        switch(sectionId) {
                            case 'home':
                                window.scrollTo({ top: 0, behavior: 'smooth' });
                                break;
                            case 'services':
                                scrollToSection('operations-section') || document.querySelector('.operations-section')?.scrollIntoView({ behavior: 'smooth' });
                                break;
                            case 'help':
                                showHelpModal();
                                break;
                            case 'about':
                                showAboutModal();
                                break;
                            case 'contact':
                                showContactModal();
                                break;
                            case 'merge':
                                highlightOperationCard('merge');
                                selectOperation('merge');
                                break;
                            case 'split':
                                highlightOperationCard('split');
                                selectOperation('split');
                                break;
                            case 'compress':
                                highlightOperationCard('compress');
                                selectOperation('compress');
                                break;
                            case 'protect':
                                highlightOperationCard('protect');
                                selectOperation('protect');
                                break;
                            case 'unlock':
                                highlightOperationCard('unlock');
                                selectOperation('unlock');
                                break;
                            case 'guide':
                                showUserGuide();
                                break;
                            case 'faq':
                                showFAQ();
                                break;
                            case 'video-help':
                                showVideoHelp();
                                break;
                            default:
                                const targetSection = document.getElementById(sectionId) || document.querySelector(`.${sectionId}-section`) || document.querySelector(`[data-section="${sectionId}"]`);
                                if (targetSection) {
                                    targetSection.scrollIntoView({ behavior: 'smooth' });
                                }
                        }
                        document.querySelectorAll('.menu-item a').forEach(a => a.classList.remove('active'));
                        this.classList.add('active');
                    }
                });
            });

            // Wire up help modal buttons
            setTimeout(() => {
                const userGuideBtn = document.getElementById('userGuideBtn');
                if (userGuideBtn) {
                    userGuideBtn.onclick = showUserGuide;
                }
                const faqBtn = document.getElementById('faqBtn');
                if (faqBtn) {
                    faqBtn.onclick = showFAQ;
                }
                const videoHelpBtn = document.getElementById('videoHelpBtn');
                if (videoHelpBtn) {
                    videoHelpBtn.onclick = showVideoHelp;
                }
            }, 500);
        });

        // Modal functions for menu items
        function showHelpModal() {
            showInfoModal('ಸಹಾಯ', `
                <h4>ಕನ್ನಡ PDF ಉಪಕರಣಗಳು - ಬಳಕೆಯ ಮಾರ್ಗದರ್ಶಿ</h4>
                <div style="text-align: left; line-height: 1.8;">
                    <h5><i class="fas fa-layer-group"></i> PDF ವಿಲೀನಗೊಳಿಸಿ:</h5>
                    <p>• ಬಹುಸಂಖ್ಯೆಯ PDF ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ<br>
                    • ಅವುಗಳು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಒಂದೇ ಫೈಲ್‌ಆಗಿ ಸಂಯೋಜಿಸಲ್ಪಡುತ್ತವೆ</p>
                    
                    <h5><i class="fas fa-cut"></i> PDF ವಿಭಾಗಿಸಿ:</h5>
                    <p>• ಒಂದು PDF ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ<br>
                    • ಪ್ರತ್ಯೇಕ ಪುಟಗಳಾಗಿ ಅಥವಾ ವ್ಯಾಪ್ತಿಗಳಾಗಿ ವಿಭಾಗಿಸಿ</p>
                    
                    <h5><i class="fas fa-compress-arrows-alt"></i> PDF ಸಂಕುಚಿಸಿ:</h5>
                    <p>• ಫೈಲ್ ಗಾತ್ರವನ್ನು ಕಡಿಮೆ ಮಾಡಿ<br>
                    • ಗುಣಮಟ್ಟವನ್ನು ಕಾಪಾಡಿಕೊಂಡು ಸಂಗ್ರಹಣೆ ಮತ್ತು ಹಂಚಿಕೆಗೆ ಸುಲಭ</p>
                    
                    <h5><i class="fas fa-shield-alt"></i> ಸುರಕ್ಷತೆ:</h5>
                    <p>• ಎಲ್ಲಾ ಫೈಲ್‌ಗಳು ನಿಮ್ಮ ಸಿಸ್ಟಮ್‌ನಲ್ಲಿಯೇ ಪ್ರಕ್ರಿಯೆಗೊಳ್ಳುತ್ತವೆ<br>
                    • ಯಾವುದೇ ಡೇಟಾ ಇಂಟರ್ನೆಟ್‌ಗೆ ಕಳುಹಿಸಲಾಗುವುದಿಲ್ಲ</p>
                </div>
            `);
        }

        function showAboutModal() {
            showInfoModal('ನಮ್ಮ ಬಗ್ಗೆ', `
                <div style="text-align: left; line-height: 1.8;">
                    <h4><i class="fas fa-landmark"></i> ಡಿಜಿಟಲ್ ಕರ್ನಾಟಕ ಇನಿಶಿಯೇಟಿವ್</h4>
                    <p>ಈ PDF ಉಪಕರಣಗಳು ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಡಿಜಿಟಲ್ ಇನಿಶಿಯೇಟಿವ್‌ನ ಭಾಗವಾಗಿ ಅಭಿವೃದ್ಧಿಪಡಿಸಲಾಗಿದೆ.</p>
                    
                    <h5><i class="fas fa-target"></i> ಉದ್ದೇಶ:</h5>
                    <p>ಸರ್ಕಾರಿ ಕೆಲಸಗಾರರಿಗೆ ಸುರಕ್ಷಿತ ಮತ್ತು ಸುಲಭವಾದ PDF ಸಂಸ್ಕರಣಾ ಸೇವೆಗಳನ್ನು ಒದಗಿಸುವುದು.</p>
                    
                    <h5><i class="fas fa-users"></i> ಲಕ್ಷ್ಯ ಗುಂಪು:</h5>
                    <p>ಕರ್ನಾಟಕ ಸರ್ಕಾರಿ ಇಲಾಖೆಗಳು ಮತ್ತು ಸರ್ಕಾರಿ ಕೆಲಸಗಾರರು</p>
                    
                    <h5><i class="fas fa-certificate"></i> ಗುಣಮಟ್ಟ ಭರವಸೆ:</h5>
                    <p>• ISO 27001 ಸುರಕ್ಷತಾ ಮಾನದಂಡಗಳ ಅನುಸರಣೆ<br>
                    • WCAG 2.1 ಪ್ರವೇಶಯೋಗ್ಯತಾ ಮಾನದಂಡಗಳು<br>
                    • ಕನ್ನಡ ಭಾಷಾ ಬೆಂಬಲ</p>
                    
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(30, 58, 138, 0.1); border-radius: 5px;">
                        <strong>ಆವೃತ್ತಿ:</strong> 2.0.0<br>
                        <strong>ಕೊನೆಯ ನವೀಕರಣ:</strong> ಜನವರಿ 2025<br>
                        <strong>ಸ್ಥಿತಿ:</strong> <span style="color: #16a34a;">🟢 ಸಕ್ರಿಯ</span>
                    </div>
                </div>
            `);
        }

        function showContactModal() {
            showInfoModal('ಸಂಪರ್ಕಿಸಿ', `
                <div style="text-align: left; line-height: 1.8;">
                    <h4><i class="fas fa-phone"></i> ತಾಂತ್ರಿಕ ಬೆಂಬಲ</h4>
                    
                    <div style="margin: 1rem 0;">
                        <strong><i class="fas fa-envelope"></i> ಇಮೇಲ್:</strong><br>
                        <a href="mailto:support@kannadapdf.kar.gov.in">support@kannadapdf.kar.gov.in</a>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <strong><i class="fas fa-phone"></i> ಫೋನ್:</strong><br>
                        080-XXXX-XXXX (ಸೋಮ-ಶುಕ್ರ, 9:00-18:00)
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <strong><i class="fas fa-map-marker-alt"></i> ವಿಳಾಸ:</strong><br>
                        ಡಿಜಿಟಲ್ ಕರ್ನಾಟಕ ವಿಭಾಗ<br>
                        ವಿಧಾನ ಸೌಧ, ಬೆಂಗಳೂರು<br>
                        ಕರ್ನಾಟಕ - 560001
                    </div>
                    
                    <h5><i class="fas fa-clock"></i> ಸೇವಾ ಸಮಯ:</h5>
                    <p>ಸೋಮವಾರ ನಿಂದ ಶುಕ್ರವಾರ: 9:00 AM - 6:00 PM<br>
                    ಶನಿ-ಭಾನುವಾರ: ಮುಚ್ಚಲಾಗಿದೆ</p>
                    
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(220, 38, 38, 0.1); border-radius: 5px;">
                        <strong><i class="fas fa-exclamation-triangle"></i> ತುರ್ತು ಸಹಾಯ:</strong><br>
                        ತುರ್ತು ತಾಂತ್ರಿಕ ಸಮಸ್ಯೆಗಳಿಗೆ, ದಯವಿಟ್ಟು ನಿಮ್ಮ IT ವಿಭಾಗವನ್ನು ಸಂಪರ್ಕಿಸಿ.
                    </div>
                </div>
            `);
        }

        function showUserGuide() {
            showInfoModal('ಬಳಕೆಯ ಮಾರ್ಗದರ್ಶಿ', `
                <div style="text-align: left; line-height: 1.8;">
                    <h4><i class="fas fa-book"></i> ವಿಸ್ತೃತ ಬಳಕೆಯ ಮಾರ್ಗದರ್ಶಿ</h4>
                    
                    <h5>1. ಫೈಲ್ ಆಯ್ಕೆ:</h5>
                    <p>• "ಆರಂಭಿಸಿ" ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ<br>
                    • ಫೈಲ್‌ಗಳನ್ನು ಎಳೆದು ಬಿಡಿ ಅಥವಾ ಬ್ರೌಸ್ ಮಾಡಿ<br>
                    • ಸರಿಯಾದ ಫಾರ್ಮ್ಯಾಟ್ ಆಯ್ಕೆ ಮಾಡಿದ್ದೀರಾ ಎಂದು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ</p>
                    
                    <h5>2. ವಿಕಲ್ಪಗಳು ಹೊಂದಿಸಿ:</h5>
                    <p>• ಪುಟ ಸಂಖ್ಯೆಗಳು, ಸಂಕುಚನ ಮಟ್ಟ ಇತ್ಯಾದಿ<br>
                    • ಪೂರ್ವವೀಕ್ಷಣೆ ವೈಶಿಷ್ಟ್ಯವನ್ನು ಬಳಸಿ<br>
                    • ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ಪರಿಶೀಲಿಸಿ</p>
                    
                    <h5>3. ಪ್ರಕ್ರಿಯೆ ಮಾಡಿ:</h5>
                    <p>• "ಪ್ರಕ್ರಿಯೆ ಮಾಡಿ" ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ<br>
                    • ಪ್ರಗತಿಗಾಗಿ ಕಾಯಿರಿ<br>
                    • ಫಲಿತಾಂಶವನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ</p>
                    
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 5px;">
                        <strong><i class="fas fa-lightbulb"></i> ಸುಝಾವುಗಳು:</strong><br>
                        • ದೊಡ್ಡ ಫೈಲ್‌ಗಳಿಗೆ ಹೆಚ್ಚು ಸಮಯ ಬೇಕಾಗಬಹುದು<br>
                        • ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕ ಅಗತ್ಯವಿಲ್ಲ<br>
                        • ಫೈಲ್‌ಗಳು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಅಳಿಸಲ್ಪಡುತ್ತವೆ
                    </div>
                </div>
            `);
        }

        function showFAQ() {
            showInfoModal('ಆಗಾಗ್ಗೆ ಕೇಳುವ ಪ್ರಶ್ನೆಗಳು', `
                <div style="text-align: left; line-height: 1.8;">
                    <h4><i class="fas fa-question-circle"></i> ಸಾಮಾನ್ಯ ಪ್ರಶ್ನೆಗಳು</h4>
                    
                    <details style="margin: 1rem 0; cursor: pointer;">
                        <summary style="font-weight: bold; color: var(--gov-blue);">Q: ಈ ಸೇವೆ ಉಚಿತವೇ?</summary>
                        <p style="margin-left: 1rem; margin-top: 0.5rem;">A: ಹೌದು, ಕರ್ನಾಟಕ ಸರ್ಕಾರಿ ಕೆಲಸಗಾರರಿಗೆ ಸಂಪೂರ್ಣವಾಗಿ ಉಚಿತ.</p>
                    </details>
                    
                    <details style="margin: 1rem 0; cursor: pointer;">
                        <summary style="font-weight: bold; color: var(--gov-blue);">Q: ಫೈಲ್ ಗಾತ್ರದ ಮಿತಿ ಎಷ್ಟು?</summary>
                        <p style="margin-left: 1rem; margin-top: 0.5rem;">A: ಪ್ರತಿ ಫೈಲ್‌ಗೆ ಗರಿಷ್ಠ 100MB ವರೆಗೆ.</p>
                    </details>
                    
                    <details style="margin: 1rem 0; cursor: pointer;">
                        <summary style="font-weight: bold; color: var(--gov-blue);">Q: ನನ್ನ ಫೈಲ್‌ಗಳು ಸುರಕ್ಷಿತವೇ?</summary>
                        <p style="margin-left: 1rem; margin-top: 0.5rem;">A: ಹೌದು, ಎಲ್ಲಾ ಪ್ರಕ್ರಿಯೆಗಳು ಸ್ಥಳೀಯವಾಗಿ ನಡೆಯುತ್ತವೆ ಮತ್ತು ಫೈಲ್‌ಗಳು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಅಳಿಸಲ್ಪಡುತ್ತವೆ.</p>
                    </details>
                    
                    <details style="margin: 1rem 0; cursor: pointer;">
                        <summary style="font-weight: bold; color: var(--gov-blue);">Q: ಕನ್ನಡ ಪಠ್ಯ ಬೆಂಬಲವಿದೆಯೇ?</summary>
                        <p style="margin-left: 1rem; margin-top: 0.5rem;">A: ಹೌದು, ಪೂರ್ಣ ಕನ್ನಡ ಯೂನಿಕೋಡ್ ಬೆಂಬಲವಿದೆ.</p>
                    </details>
                    
                    <details style="margin: 1rem 0; cursor: pointer;">
                        <summary style="font-weight: bold; color: var(--gov-blue);">Q: ಮೊಬೈಲ್ ಫೋನ್‌ನಲ್ಲಿ ಬಳಸಬಹುದೇ?</summary>
                        <p style="margin-left: 1rem; margin-top: 0.5rem;">A: ಹೌದು, ಆದರೆ ಸಂಪೂರ್ಣ ಅನುಭವಕ್ಕಾಗಿ ಕಂಪ್ಯೂಟರ್ ಬಳಸಿ.</p>
                    </details>
                    
                    <details style="margin: 1rem 0; cursor: pointer;">
                        <summary style="font-weight: bold; color: var(--gov-blue);">Q: ತಾಂತ್ರಿಕ ಸಮಸ್ಯೆಯಾದರೆ ಏನು ಮಾಡಬೇಕು?</summary>
                        <p style="margin-left: 1rem; margin-top: 0.5rem;">A: "ಸಂಪರ್ಕಿಸಿ" ವಿಭಾಗದಲ್ಲಿ ಅಡಿದ ಮಾಹಿತಿಯನ್ನು ಬಳಸಿ ಸಹಾಯ ಪಡೆಯಿರಿ.</p>
                    </details>
                </div>
            `);
        }

        function showVideoHelp() {
            showInfoModal('ವೀಡಿಯೋ ಟ್ಯುಟೋರಿಯಲ್', `
                <div style="text-align: center; line-height: 1.8;">
                    <h4><i class="fas fa-video"></i> ವೀಡಿಯೋ ಮಾರ್ಗದರ್ಶಿಗಳು</h4>
                    
                    <div style="margin: 2rem 0;">
                        <i class="fas fa-play-circle" style="font-size: 4rem; color: var(--gov-blue); margin-bottom: 1rem;"></i>
                        <h5>ವೀಡಿಯೋ ಟ್ಯುಟೋರಿಯಲ್‌ಗಳು ಶೀಘ್ರದಲ್ಲೇ ಲಭ್ಯವಾಗಲಿವೆ!</h5>
                        <p>ನಾವು ಈ ಕೆಳಗಿನ ವಿಷಯಗಳ ಮೇಲೆ ವೀಡಿಯೋ ಮಾರ್ಗದರ್ಶಿಗಳನ್ನು ತಯಾರಿಸುತ್ತಿದ್ದೇವೆ:</p>
                    </div>
                    
                    <div style="text-align: left; margin: 1rem 0;">
                        <ul style="list-style: none; padding: 0;">
                            <li style="margin: 0.5rem 0;"><i class="fas fa-video text-primary"></i> PDF ವಿಲೀನಗೊಳಿಸುವಿಕೆ</li>
                            <li style="margin: 0.5rem 0;"><i class="fas fa-video text-primary"></i> PDF ವಿಭಾಗಿಸುವಿಕೆ</li>
                            <li style="margin: 0.5rem 0;"><i class="fas fa-video text-primary"></i> ಸಂಕುಚನ ತಂತ್ರಗಳು</li>
                            <li style="margin: 0.5rem 0;"><i class="fas fa-video text-primary"></i> PDF ರಕ್ಷಣೆ ಮತ್ತು ಅನ್‌ಲಾಕ್</li>
                            <li style="margin: 0.5rem 0;"><i class="fas fa-video text-primary"></i> ಫಾರ್ಮ್ಯಾಟ್ ಪರಿವರ್ತನೆ</li>
                        </ul>
                    </div>
                    
                    <div style="margin-top: 2rem; padding: 1rem; background: rgba(30, 58, 138, 0.1); border-radius: 5px;">
                        <p><strong>ಅಪ್‌ಡೇಟ್ ಪಡೆಯಲು:</strong><br>
                        support@kannadapdf.kar.gov.in ನಲ್ಲಿ ನಿಮ್ಮ ಇಮೇಲ್ ಅಡ್ರೆಸ್ ನೋಂದಾಯಿಸಿ</p>
                    </div>
                </div>
            `);
        }

        // Generic info modal function
        function showInfoModal(title, content) {
            // Create modal if it doesn't exist
            let infoModal = document.getElementById('infoModal');
            if (!infoModal) {
                infoModal = document.createElement('div');
                infoModal.id = 'infoModal';
                infoModal.className = 'modal';
                infoModal.innerHTML = `
                    <div class="modal-content" style="max-width: 600px; max-height: 80vh; overflow-y: auto;">
                        <div class="modal-header">
                            <h3 class="modal-title" id="infoModalTitle">${title}</h3>
                            <span class="close" onclick="closeInfoModal()">&times;</span>
                        </div>
                        <div class="modal-body" id="infoModalBody">
                            ${content}
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-primary" onclick="closeInfoModal()">ಮುಚ್ಚಿ</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(infoModal);
            } else {
                document.getElementById('infoModalTitle').textContent = title;
                document.getElementById('infoModalBody').innerHTML = content;
            }
            
            infoModal.style.display = 'block';
        }

        function closeInfoModal() {
            const infoModal = document.getElementById('infoModal');
            if (infoModal) {
                infoModal.style.display = 'none';
            }
        }

        // Highlight operation card when accessed from menu
        function highlightOperationCard(operationId) {
            // First scroll to services section
            const servicesSection = document.getElementById('services');
            if (servicesSection) {
                servicesSection.scrollIntoView({ behavior: 'smooth' });
            }
            
            // Remove previous highlights
            document.querySelectorAll('.operation-card').forEach(card => {
                card.classList.remove('highlighted');
            });
            
            // Highlight the target card
            setTimeout(() => {
                const targetCard = document.getElementById(operationId) || 
                                 document.querySelector(`[data-operation="${operationId}"]`);
                if (targetCard) {
                    targetCard.classList.add('highlighted');
                    targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    // Remove highlight after 3 seconds
                    setTimeout(() => {
                        targetCard.classList.remove('highlighted');
                    }, 3000);
                }
            }, 500);
        }
   

    document.addEventListener('DOMContentLoaded', function() {
        // Ensure all modals are hidden on page load
        document.getElementById('operationModal').style.display = 'none';
        document.getElementById('previewModal').style.display = 'none';
        document.getElementById('loadingModal').style.display = 'none';
        
        // Ensure main content is visible
        const container = document.querySelector('.container');
        const operationsSection = document.querySelector('.operations-section');
        const operationsGrid = document.querySelector('.operations-grid');
        
        if (container) {
            container.style.display = 'block';
            container.style.visibility = 'visible';
        }
        if (operationsSection) {
            operationsSection.style.display = 'block';
            operationsSection.style.visibility = 'visible';
        }
        if (operationsGrid) {
            operationsGrid.style.display = 'grid';
            operationsGrid.style.visibility = 'visible';
        }
        
        // Initialize language dropdown
        initializeLanguageDropdown();
    });
 });