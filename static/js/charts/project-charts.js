/**
 * Project Chart Functionality
 * This file handles chart rendering for project details page
 */

function initializeProjectCharts(chartData) {
    // Initialize Category chart if we have data
    if (chartData.categoryLabels && chartData.categoryLabels.length > 0) {
        var ctxCategory = document.getElementById('categoryChart');
        if (ctxCategory) {
            new Chart(ctxCategory.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: chartData.categoryLabels,
                    datasets: [{
                        data: chartData.categoryValues,
                        backgroundColor: [
                            '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
                            '#6610f2', '#fd7e14', '#20c997', '#e83e8c', '#6c757d'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Initialize Status chart if we have data
    if (chartData.statusLabels && chartData.statusLabels.length > 0) {
        var ctxStatus = document.getElementById('statusChart');
        if (ctxStatus) {
            new Chart(ctxStatus.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: chartData.statusLabels,
                    datasets: [{
                        data: chartData.statusValues,
                        backgroundColor: [
                            '#ffc107', // New
                            '#17a2b8', // Acknowledged
                            '#007bff', // In Progress
                            '#28a745', // Implemented
                            '#6c757d'  // Archived
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12
                            }
                        }
                    }
                }
            });
        }
    }
}

// This will be called from the template when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if chartDataElement exists
    const chartDataElement = document.getElementById('projectChartData');
    if (chartDataElement) {
        try {
            const chartData = JSON.parse(chartDataElement.textContent);
            initializeProjectCharts(chartData);
        } catch (e) {
            console.error("Error initializing project charts:", e);
        }
    }
});