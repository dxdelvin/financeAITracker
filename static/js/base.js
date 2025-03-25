document.addEventListener('DOMContentLoaded', function() {
    // Auto-open form if there's initial AI data
    const initialDataElement = document.getElementById('form-initial-data');
    if (initialDataElement && initialDataElement.dataset.hasInitial === 'true') {
        const aiForm = document.getElementById('transactionFormOverlay1');
        if (aiForm) aiForm.style.display = 'flex';
    }

    // Form toggle handler
    function toggleForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.style.display = form.style.display === 'flex' ? 'none' : 'flex';
        }
    }

    // Clear AI session cookie
    function clearAISession() {
        document.cookie = 'ai_transaction_data=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    }

    // Event delegation for all form buttons
    document.body.addEventListener('click', function(e) {
        // Open Transaction Form 1
        if (e.target.matches('#openTransactionForm1')) {
            toggleForm('transactionFormOverlay1');
        }
        // Close Transaction Form 1 (AI Form)
        else if (e.target.matches('#cancelBtn1')) {
            toggleForm('transactionFormOverlay1');
            clearAISession(); // Clear cookie when canceling AI form
        }
        // Open Transaction Form 2
        else if (e.target.matches('#openTransactionForm2')) {
            toggleForm('transactionFormOverlay2');
        }
        // Close Transaction Form 2
        else if (e.target.matches('#cancelBtn2')) {
            toggleForm('transactionFormOverlay2');
        }
    });

    // Real-time character counter for comment field
    const commentField = document.getElementById('id_comment');
    const charCount = document.getElementById('charCount');

    if (commentField && charCount) {
        commentField.addEventListener('input', function() {
            const currentLength = this.value.length;
            const maxLength = this.maxLength;
            charCount.textContent = `${currentLength}/${maxLength}`;

            // Visual feedback when approaching limit
            charCount.style.color = currentLength > maxLength * 0.9
                ? '#ef4444'
                : '#6b7280';
        });

        // Trigger initial count
        commentField.dispatchEvent(new Event('input'));
    }
});