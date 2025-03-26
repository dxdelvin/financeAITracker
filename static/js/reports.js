document.addEventListener("DOMContentLoaded", function () {
    console.log("Reports page loaded");

    const chartData = document.getElementById("chart-data");
    const totalIncome = parseFloat(chartData.dataset.totalIncome);
    const totalExpenses = parseFloat(chartData.dataset.totalExpenses);

    let transactions = [];
    try {
        transactions = JSON.parse(chartData.dataset.transactions.replace(/'/g, '"'));
    } catch (error) {
        console.error("Error parsing transactions JSON:", error);
    }

    console.log("Total Income:", totalIncome);
    console.log("Total Expenses:", totalExpenses);
    console.log("Transactions:", transactions);

    updateProgressBars(totalIncome, totalExpenses);
    populateTransactionTable(transactions);
    setupFilters();
});

// Update progress bars dynamically
function updateProgressBars(income, expenses) {
    const maxValue = Math.max(income, expenses);
    if (maxValue > 0) {
        document.getElementById("income-progress").style.width = `${(income / maxValue) * 100}%`;
        document.getElementById("expenses-progress").style.width = `${(expenses / maxValue) * 100}%`;
    }
}

// Populate Transaction Table
function populateTransactionTable(transactions) {
    const tbody = document.getElementById("transaction-body");
    tbody.innerHTML = "";

    if (!transactions || transactions.length === 0) {
        tbody.innerHTML = "<tr><td colspan='4'>No transactions found</td></tr>";
        return;
    }

    transactions.forEach(txn => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${txn.date_created}</td>
            <td>${txn.transaction_type}</td>
            <td>${txn.category}</td>
            <td>$${txn.amount.toFixed(2)}</td>
        `;
        tbody.appendChild(row);
    });
}

// Set up filter button functionality
function setupFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const applyCustomButton = document.getElementById('applyCustom');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    // Handle predefined filters (Last 7 Days, Last 30 Days, etc.)
    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            setActiveFilter(button);
            applyFilter(button.dataset.days);
        });
    });

    // Handle custom date range filter
    applyCustomButton.addEventListener('click', function () {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;

        if (startDate && endDate) {
            applyFilter('custom', startDate, endDate);
        } else {
            alert('Please select both start and end dates.');
        }
    });

    // Set active filter based on URL parameters
    setActiveFilterFromUrl();
}

// Apply filter and reload page with new parameters
function applyFilter(days, startDate = null, endDate = null) {
    let url = new URL(window.location.href);
    if (days === 'custom') {
        url.searchParams.set('startDate', startDate);
        url.searchParams.set('endDate', endDate);
    } else {
        url.searchParams.set('days', days);
    }
    window.location.href = url.toString();
}

// Set active button style
function setActiveFilter(activeButton) {
    document.querySelectorAll('.filter-btn').forEach(button => button.classList.remove('active'));
    activeButton.classList.add('active');
}

// Highlight the correct filter button on page load
function setActiveFilterFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const days = urlParams.get('days');

    document.querySelectorAll('.filter-btn').forEach(button => {
        if (button.dataset.days === days) {
            setActiveFilter(button);
        }
    });
}
