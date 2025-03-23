document.addEventListener("DOMContentLoaded", function() {
    // Get the button and form container elements
    const openButton = document.getElementById("openTransactionForm");
    const transactionFormContainer = document.getElementById("transactionFormOverlay");

    // Add event listener to open the form when the button is clicked
    openButton.addEventListener("click", function() {
        transactionFormContainer.style.display = "flex";

    });

    // Add event listener to close the form when the cancel button is clicked
    const cancelButton = document.getElementById("cancelBtn");
    cancelButton.addEventListener("click", function() {
        transactionFormContainer.style.display = "none";
    });
});

function updateCharCount() {
    let inputField = document.getElementById("comment");
    let charCount = inputField.value.length;
    let maxLength = inputField.getAttribute("maxlength");
    document.getElementById("charCount").innerText = charCount + "/" + maxLength;
}