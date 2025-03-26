document.addEventListener("DOMContentLoaded", function () {
    // Get the filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    const applyCustomButton = document.getElementById('applyCustom');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    // Event listener for predefined filters (Last 7 Days, Last 30 Days, etc.)
    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to the clicked button
            button.classList.add('active');

            // Get the number of days or custom filter type
            const days = button.getAttribute('data-days');

            // Update the URL or fetch data based on selected filter
            applyFilter(days);
        });
    });

    // Event listener for custom date range filter
    applyCustomButton.addEventListener('click', function () {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;

        if (startDate && endDate) {
            applyFilter('custom', startDate, endDate);
        } else {
            alert('Please select both start and end dates.');
        }
    });

    // Function to apply the selected filter and update the page
    function applyFilter(days, startDate = null, endDate = null) {
        // Prepare the URL parameters based on the selected filter
        let url = new URL(window.location.href);
        if (days === 'custom') {
            url.searchParams.set('startDate', startDate);
            url.searchParams.set('endDate', endDate);
        } else {
            url.searchParams.set('days', days);
        }

        // Reload the page with the updated filter parameters
        window.location.href = url.toString();
    }

    // Add the active class to the filter button based on the URL parameter
    function setActiveFilterFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const days = urlParams.get('days');

        if (days) {
            filterButtons.forEach(button => {
                // Remove active class from all buttons
                button.classList.remove('active');
                // Add active class to the corresponding button based on the "days" parameter
                if (button.getAttribute('data-days') === days) {
                    button.classList.add('active');
                }
            });
        }
    }

    // Set the active filter on page load
    setActiveFilterFromUrl();
});
