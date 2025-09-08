document.addEventListener('DOMContentLoaded', function() {
    // Deforestation Trend Chart
    const trendCtx = document.getElementById('deforestationTrendChart');
    
    if (trendCtx) {
        const trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Forest Loss (hectares)',
                    data: [420, 532, 680, 790, 850, 920, 1100, 1250, 1180, 1050, 980, 890],
                    backgroundColor: 'rgba(244, 67, 54, 0.2)',
                    borderColor: 'rgba(244, 67, 54, 1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(244, 67, 54, 1)',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }, {
                    label: 'Forest Gain (hectares)',
                    data: [120, 150, 180, 210, 240, 260, 280, 320, 350, 380, 410, 440],
                    backgroundColor: 'rgba(76, 175, 80, 0.2)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(76, 175, 80, 1)',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Hectares'
                        }
                    }
                }
            }
        });
        
        // Update chart when period selector changes
        const trendPeriod = document.getElementById('trendPeriod');
        trendPeriod.addEventListener('change', function() {
            let labels, lossData, gainData;
            
            switch(this.value) {
                case 'monthly':
                    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    lossData = [420, 532, 680, 790, 850, 920, 1100, 1250, 1180, 1050, 980, 890];
                    gainData = [120, 150, 180, 210, 240, 260, 280, 320, 350, 380, 410, 440];
                    break;
                case 'quarterly':
                    labels = ['Q1', 'Q2', 'Q3', 'Q4'];
                    lossData = [1632, 2560, 3530, 2920];
                    gainData = [450, 710, 950, 1230];
                    break;
                case 'yearly':
                    labels = ['2018', '2019', '2020', '2021', '2022', '2023'];
                    lossData = [4200, 5800, 7500, 9200, 10640, 12450];
                    gainData = [1200, 1800, 2400, 3100, 3340, 4100];
                    break;
            }
            
            trendChart.data.labels = labels;
            trendChart.data.datasets[0].data = lossData;
            trendChart.data.datasets[1].data = gainData;
            trendChart.update();
        });
    }
    
    // Forest Cover by Region Chart
    const coverCtx = document.getElementById('forestCoverChart');
    
    if (coverCtx) {
        const coverChart = new Chart(coverCtx, {
            type: 'doughnut',
            data: {
                labels: ['Dense Forest', 'Moderate Forest', 'Open Forest', 'Scrubland', 'Non-Forest'],
                datasets: [{
                    data: [35, 25, 15, 10, 15],
                    backgroundColor: [
                        'rgba(46, 125, 50, 0.8)',
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(139, 195, 74, 0.8)',
                        'rgba(205, 220, 57, 0.8)',
                        'rgba(255, 152, 0, 0.8)'
                    ],
                    borderColor: [
                        'rgba(46, 125, 50, 1)',
                        'rgba(76, 175, 80, 1)',
                        'rgba(139, 195, 74, 1)',
                        'rgba(205, 220, 57, 1)',
                        'rgba(255, 152, 0, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Comparison Chart (in Analysis section)
    const comparisonCtx = document.getElementById('comparisonChart');
    
    if (comparisonCtx) {
        const comparisonChart = new Chart(comparisonCtx, {
            type: 'bar',
            data: {
                labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
                datasets: [{
                    label: 'Forest Cover (hectares)',
                    data: [125000, 119200, 111700, 102500, 91860, 82500],
                    backgroundColor: 'rgba(46, 125, 50, 0.7)',
                    borderColor: 'rgba(46, 125, 50, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Hectares'
                        }
                    }
                }
            }
        });
    }
    
    // Deforestation by Cause Chart (would be in a detailed report)
    function createCauseChart() {
        const ctx = document.createElement('canvas');
        const container = document.querySelector('.tab-pane#details');
        const chartContainer = document.createElement('div');
        chartContainer.style.height = '300px';
        chartContainer.appendChild(ctx);
        container.appendChild(chartContainer);
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Agriculture', 'Logging', 'Infrastructure', 'Mining', 'Urban Expansion', 'Other'],
                datasets: [{
                    data: [40, 20, 15, 10, 10, 5],
                    backgroundColor: [
                        'rgba(244, 67, 54, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(255, 235, 59, 0.8)',
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(33, 150, 243, 0.8)',
                        'rgba(156, 39, 176, 0.8)'
                    ],
                    borderColor: [
                        'rgba(244, 67, 54, 1)',
                        'rgba(255, 152, 0, 1)',
                        'rgba(255, 235, 59, 1)',
                        'rgba(76, 175, 80, 1)',
                        'rgba(33, 150, 243, 1)',
                        'rgba(156, 39, 176, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Add cause chart when details tab is clicked
    const detailsTabBtn = document.querySelector('.tab-btn[data-tab="details"]');
    detailsTabBtn.addEventListener('click', function() {
        // Only create the chart once
        if (!document.querySelector('#details canvas')) {
            setTimeout(createCauseChart, 100);
        }
    });
    
    // Function to create a time series chart for a specific region
    function createRegionTimeSeries(regionName, data) {
        const canvas = document.createElement('canvas');
        const container = document.createElement('div');
        container.style.marginTop = '20px';
        container.style.height = '250px';
        container.appendChild(canvas);
        
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: `${regionName} Forest Cover`,
                    data: data.values,
                    backgroundColor: 'rgba(46, 125, 50, 0.2)',
                    borderColor: 'rgba(46, 125, 50, 1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Forest Cover (%)'
                        }
                    }
                }
            }
        });
        
        return container;
    }
    
    // Function to create a deforestation risk chart
    function createRiskChart() {
        const ctx = document.createElement('canvas');
        const container = document.createElement('div');
        container.style.marginTop = '20px';
        container.style.height = '250px';
        container.appendChild(ctx);
        
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: [
                    'Illegal Logging',
                    'Agricultural Expansion',
                    'Wildfire Risk',
                    'Mining Activity',
                    'Infrastructure Development',
                    'Climate Change Impact'
                ],
                datasets: [{
                    label: 'Current Risk Level',
                    data: [85, 75, 60, 50, 65, 70],
                    backgroundColor: 'rgba(244, 67, 54, 0.2)',
                    borderColor: 'rgba(244, 67, 54, 0.8)',
                    pointBackgroundColor: 'rgba(244, 67, 54, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(244, 67, 54, 1)'
                }, {
                    label: '5-Year Projection',
                    data: [90, 85, 75, 65, 80, 85],
                    backgroundColor: 'rgba(255, 152, 0, 0.2)',
                    borderColor: 'rgba(255, 152, 0, 0.8)',
                    pointBackgroundColor: 'rgba(255, 152, 0, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(255, 152, 0, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                }
            }
        });
        
        return container;
    }
    
    // Function to update all charts with new data
    function updateChartsWithData(newData) {
        // This would be called when new data is loaded from the backend
        console.log('Updating charts with new data:', newData);
        
        // In a real implementation, you would update each chart with the new data
        // For example:
        // trendChart.data.labels = newData.trend.labels;
        // trendChart.data.datasets[0].data = newData.trend.loss;
        // trendChart.update();
    }
    
    // Expose update function to global scope for backend to call
    window.updateChartsWithData = updateChartsWithData;
});