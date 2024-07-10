document.addEventListener('DOMContentLoaded', function () {
    const categoryData = JSON.parse(document.getElementById('categoryData').textContent);
    const yearlyData = JSON.parse(document.getElementById('yearlyData').textContent);

    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    const categoryChart = new Chart(categoryCtx, {
        type: 'pie',
        data: {
            labels: categoryData.map(item => item[0]),
            datasets: [{
                data: categoryData.map(item => item[1]),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)'
                ],
                borderColor: [
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: 'rgba(255, 255, 255, 1)'  // Set legend text color to white
                    }
                }
            }
        }
    });

    const yearlyContainer = document.getElementById('yearlyCharts');
    const monthlyLabels = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

    const expensesByYear = {};
    yearlyData.forEach(item => {
        const [year, yearMonth, amount] = item;
        if (!expensesByYear[year]) {
            expensesByYear[year] = new Array(12).fill(0);
        }
        const monthIndex = parseInt(yearMonth.split('-')[1], 10) - 1;
        expensesByYear[year][monthIndex] = amount;
    });

    Object.keys(expensesByYear).forEach(year => {
        const chartId = `chart-${year}`;
        const chartCanvas = document.createElement('canvas');
        chartCanvas.id = chartId;
        yearlyContainer.appendChild(chartCanvas);

        const ctx = document.getElementById(chartId).getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: monthlyLabels,
                datasets: [{
                    label: `Expenses for ${year}`,
                    data: expensesByYear[year],
                    backgroundColor: 'rgba(255, 206, 86, 0.8)',
                    borderColor: 'rgba(255, 255, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: 'rgba(255, 255, 255, 1)'  // Set y-axis text color to white
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.2)'  // Set y-axis grid color
                        }
                    },
                    x: {
                        ticks: {
                            color: 'rgba(255, 255, 255, 1)'  // Set x-axis text color to white
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.2)'  // Set x-axis grid color
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'rgba(255, 255, 255, 1)'  // Set legend text color to white
                        }
                    }
                }
            }
        });
    });
});
