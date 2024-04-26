let currentChartType = 'bar'; // Default chart type
let chartInstance; // To keep track of the created chart instance

// document.addEventListener('DOMContentLoaded', function() {
//     fetchDataAndRenderChart();

//     document.getElementById('chartToggle').addEventListener('change', function() {
//         currentChartType = this.checked ? 'pie' : 'bar';
//         fetchDataAndRenderChart(); // Re-fetch data and re-render chart
//     });
// });

document.addEventListener('DOMContentLoaded', function() {
    createChart(classificationData);

    document.getElementById('chartToggle').addEventListener('change', function() {
        currentChartType = this.checked ? 'pie' : 'bar';
        createChart(classificationData);
    });
});

function fetchDataAndRenderChart() {
    fetch('/your-api-endpoint/') // Replace with your actual API endpoint
        .then(response => response.json())
        .then(data => {
            createChart(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function createChart(data) {
    const ctx = document.getElementById('classificationChart').getContext('2d');
    const labels = Object.keys(data);
    const values = Object.values(data);

    // Destroy the previous chart instance if it exists
    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: currentChartType,
        data: {
            labels: labels,
            datasets: [{
                label: 'Classification Counts',
                data: values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                    'rgba(255, 159, 64, 0.5)',
                    'rgba(100, 159, 64, 0.5)'
                ],
                hoverOffset: 4
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    display: currentChartType === 'bar'
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += currentChartType === 'bar' ? context.parsed.y : context.parsed;
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}