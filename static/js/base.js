document.addEventListener('DOMContentLoaded', function() {
    // Safe JSON parsing with error handling
    function safeParse(jsonString, fallback) {
        if (!jsonString || jsonString.trim() === '') {
            return fallback;
        }
        try {
            const parsed = JSON.parse(jsonString);
            return Array.isArray(parsed) && parsed.length ? parsed : fallback;
        } catch (e) {
            console.error('JSON parse error:', e, 'for string:', jsonString);
            return fallback;
        }
    }

    // Get the data container safely
    const chartDataEl = document.getElementById('chart-data');
    if (!chartDataEl) {
        console.error('Chart data container not found!');
        return;
    }

    // Get all chart data with fallbacks
    const chartData = {
        categories: safeParse(chartDataEl.dataset.categories, ['No Data']),
        categoryAmounts: safeParse(chartDataEl.dataset.categoryAmounts, [0]),
        months: safeParse(chartDataEl.dataset.months, ['Jan 2023']),
        monthlyIncome: safeParse(chartDataEl.dataset.monthlyIncome, [0]),
        monthlyExpenses: safeParse(chartDataEl.dataset.monthlyExpenses, [0]),
        totalIncome: parseFloat(chartDataEl.dataset.totalIncome || 0),
        totalExpenses: parseFloat(chartDataEl.dataset.totalExpenses || 0)
    };
    console.log('Chart data loaded:', chartData);


    // 1. Income vs Expenses Bar Chart
    new Chart(document.getElementById('incomeExpenseChart'), {
        type: 'bar',
        data: {
            labels: ['Income', 'Expenses'],
            datasets: [{
                label: 'Amount ($)',
                data: [chartData.totalIncome, chartData.totalExpenses],
                backgroundColor: ['#10b981', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });

    // 2. Category Breakdown Doughnut Chart
    new Chart(document.getElementById('categoryChart'), {
        type: 'doughnut',
        data: {
            labels: chartData.categories,
            datasets: [{
                data: chartData.categoryAmounts,
                backgroundColor: [
                    '#3b82f6', '#10b981', '#f59e0b',
                    '#8b5cf6', '#ef4444', '#6366f1',
                    '#ec4899', '#14b8a6', '#f97316'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });

    // 3. Monthly Trends Line Chart
    new Chart(document.getElementById('trendChart'), {
        type: 'line',
        data: {
            labels: chartData.months,
            datasets: [
                {
                    label: 'Income',
                    data: chartData.monthlyIncome,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Expenses',
                    data: chartData.monthlyExpenses,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
});