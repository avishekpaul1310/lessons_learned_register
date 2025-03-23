// Main JavaScript for Lessons Learned System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    const confirmDeleteForms = document.querySelectorAll('.confirm-delete-form');
    confirmDeleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Handle attachment upload field
    const attachmentInput = document.getElementById('id_file');
    if (attachmentInput) {
        attachmentInput.addEventListener('change', function() {
            const fileNameDisplay = document.getElementById('file-name-display');
            if (fileNameDisplay) {
                if (this.files.length > 0) {
                    fileNameDisplay.textContent = this.files[0].name;
                } else {
                    fileNameDisplay.textContent = 'No file chosen';
                }
            }
        });
    }

    // Handle status change
    const statusSelect = document.getElementById('id_status');
    const implementationNotesField = document.getElementById('div_id_implementation_notes');
    
    if (statusSelect && implementationNotesField) {
        // Show/hide implementation notes based on status
        function toggleImplementationNotes() {
            if (statusSelect.value === 'IMPLEMENTED') {
                implementationNotesField.style.display = 'block';
            } else {
                implementationNotesField.style.display = 'none';
            }
        }
        
        // Initial check
        toggleImplementationNotes();
        
        // Add event listener
        statusSelect.addEventListener('change', toggleImplementationNotes);
    }
});