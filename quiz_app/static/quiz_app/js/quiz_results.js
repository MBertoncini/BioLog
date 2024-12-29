document.addEventListener('DOMContentLoaded', function() {
    const speciesItems = document.querySelectorAll('.species-item');
    let maxErrorCount = 0;

    // Trova il conteggio di errori massimo
    speciesItems.forEach(item => {
        const errorCount = parseInt(item.dataset.errorCount);
        if (errorCount > maxErrorCount) {
            maxErrorCount = errorCount;
        }
    });

    // Imposta la larghezza della barra di progresso per ogni specie
    speciesItems.forEach(item => {
        const errorCount = parseInt(item.dataset.errorCount);
        const percentage = (errorCount / maxErrorCount) * 100;
        const progressBar = item.querySelector('.progress');
        progressBar.style.width = `${percentage}%`;
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Grafico Accuratezza
    const accuracyCtx = document.getElementById('accuracyChart').getContext('2d');
    new Chart(accuracyCtx, {
        type: 'pie',
        data: {
            labels: ['Corrette', 'Errate'],
            datasets: [{
                data: [correctAnswers, incorrectAnswers],
                backgroundColor: ['#4CAF50', '#F44336']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                }
            }
        }
    });

    // Grafico Prestazioni nel tempo
    const performanceCtx = document.getElementById('performanceChart').getContext('2d');
    let performanceChart;

    function updatePerformanceChart(days) {
        fetch(`/quiz/performance_data/${days}/`)
            .then(response => response.json())
            .then(data => {
                if (performanceChart) {
                    performanceChart.destroy();
                }

                performanceChart = new Chart(performanceCtx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Accuratezza (%)',
                            data: data.accuracies,
                            borderColor: '#3498db',
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: `Prestazioni negli ultimi ${days} giorni`
                            }
                        }
                    }
                });
            });
    }

    document.getElementById('last7Days').addEventListener('click', () => updatePerformanceChart(7));
    document.getElementById('last30Days').addEventListener('click', () => updatePerformanceChart(30));

    // Inizializza con gli ultimi 7 giorni
    updatePerformanceChart(7);
});

document.querySelectorAll('.achievement-item').forEach(item => {
    const tooltip = document.createElement('div');
    tooltip.classList.add('achievement-tooltip');
    tooltip.textContent = item.title;
    item.appendChild(tooltip);
});