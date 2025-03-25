document.addEventListener('DOMContentLoaded', function() {
    // Safely parse data with fallbacks
    function safeParse(jsonString, fallback) {
        try {
            return JSON.parse(jsonString);
        } catch (e) {
            console.error('Failed to parse JSON:', e);
            return fallback;
        }
    }

    // Get chart data with fallback values
    const chartData = {
        categories: safeParse('{{ categories|escapejs }}', ['No Data']),
        categoryAmounts: safeParse('{{ category_amounts|escapejs }}', [0]),
        months: safeParse('{{ months|escapejs }}', ['Jan 2023']),
        monthlyIncome: safeParse('{{ monthly_income|escapejs }}', [0]),
        monthlyExpenses: safeParse('{{ monthly_expenses|escapejs }}', [0]),
        totalIncome: parseFloat('{{ total_income|default:0 }}'),
        totalExpenses: parseFloat('{{ total_expenses|default:0 }}')
    };

    // Initialize charts with the safe data
    new Chart(document.getElementById('categoryChart'), {
        type: 'doughnut',
        data: {
            labels: chartData.categories,
            datasets: [{
                data: chartData.categoryAmounts,
                backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']
            }]
        }
    });

    new Chart(document.getElementById('trendChart'), {
        type: 'line',
        data: {
            labels: chartData.months,
            datasets: [
                {
                    label: 'Income',
                    data: chartData.monthlyIncome,
                    borderColor: '#10b981',
                    tension: 0.1
                },
                {
                    label: 'Expenses',
                    data: chartData.monthlyExpenses,
                    borderColor: '#ef4444',
                    tension: 0.1
                }
            ]
        }
    });
});