/**
 * Dashboard Charts & Animations
 * Uses Chart.js for pie, bar, and line charts with auto-refresh.
 */

document.addEventListener('DOMContentLoaded', function () {
    // ─── Count-Up Animation ───
    animateCounters();

    // ─── Load Charts ───
    const config = window.dashboardConfig || {};
    loadDiseaseChart(config.diseaseChartUrl, config.period);
    loadVisitTrendChart(config.visitTrendUrl);

    // ─── Auto-refresh every 5 minutes ───
    setInterval(function () {
        loadDiseaseChart(config.diseaseChartUrl, config.period);
        loadVisitTrendChart(config.visitTrendUrl);
    }, 300000);
});


// ═══════════════════════════════════════════════════════════════
// Count-Up Animation
// ═══════════════════════════════════════════════════════════════
function animateCounters() {
    const counters = document.querySelectorAll('.count-up');
    const duration = 1500; // ms

    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target')) || 0;
        if (target === 0) { counter.textContent = '0'; return; }

        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(eased * target);

            counter.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    });
}


// ═══════════════════════════════════════════════════════════════
// Disease Charts (Pie + Bar)
// ═══════════════════════════════════════════════════════════════
let pieChart = null;
let barChart = null;

function loadDiseaseChart(url, period) {
    if (!url) return;

    const fullUrl = url + '?period=' + (period || 'overall');

    fetch(fullUrl, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
        renderPieChart(data.pie);
        renderBarChart(data.bar);
    })
    .catch(err => console.error('Disease chart error:', err));
}

function renderPieChart(data) {
    const ctx = document.getElementById('diseasePieChart');
    if (!ctx) return;

    if (pieChart) pieChart.destroy();

    if (!data.labels || data.labels.length === 0) {
        ctx.parentElement.innerHTML = '<p class="text-muted text-center">No disease data available</p>';
        return;
    }

    pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: data.colors || [
                    '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e',
                    '#e74a3b', '#858796', '#5a5c69', '#2e59d9'
                ],
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: { size: 11, family: 'Inter' }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,.8)',
                    padding: 12,
                    titleFont: { size: 13, family: 'Inter', weight: '600' },
                    bodyFont: { size: 12, family: 'Inter' },
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((context.parsed / total) * 100).toFixed(1);
                            return ` ${context.label}: ${context.parsed} (${pct}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1200,
            }
        }
    });
}

function renderBarChart(data) {
    const ctx = document.getElementById('diseaseBarChart');
    if (!ctx) return;

    if (barChart) barChart.destroy();

    if (!data.labels || data.labels.length === 0) {
        ctx.parentElement.innerHTML = '<p class="text-muted text-center">No disease data available</p>';
        return;
    }

    // Gradient fill
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(78, 115, 223, 0.8)');
    gradient.addColorStop(1, 'rgba(78, 115, 223, 0.2)');

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels.map(l => l.length > 18 ? l.substring(0, 18) + '…' : l),
            datasets: [{
                label: 'Cases',
                data: data.data,
                backgroundColor: gradient,
                borderColor: '#4e73df',
                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,.8)',
                    padding: 10,
                    titleFont: { size: 12, family: 'Inter' },
                    bodyFont: { size: 11, family: 'Inter' },
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { display: false },
                    ticks: { font: { size: 11, family: 'Inter' } }
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 10, family: 'Inter' } }
                }
            },
            animation: { duration: 1000 }
        }
    });
}


// ═══════════════════════════════════════════════════════════════
// Visit Trend (Line Chart)
// ═══════════════════════════════════════════════════════════════
let trendChart = null;

function loadVisitTrendChart(url) {
    if (!url) return;

    fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => renderTrendChart(data))
    .catch(err => console.error('Trend chart error:', err));
}

function renderTrendChart(data) {
    const ctx = document.getElementById('visitTrendChart');
    if (!ctx) return;

    if (trendChart) trendChart.destroy();

    if (!data.labels || data.labels.length === 0) {
        ctx.parentElement.innerHTML = '<p class="text-muted text-center">No visit data available</p>';
        return;
    }

    // Area gradient
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 280);
    gradient.addColorStop(0, 'rgba(54, 185, 204, 0.3)');
    gradient.addColorStop(1, 'rgba(54, 185, 204, 0.02)');

    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Visits',
                data: data.data,
                fill: true,
                backgroundColor: gradient,
                borderColor: '#36b9cc',
                borderWidth: 2.5,
                pointBackgroundColor: '#36b9cc',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 6,
                tension: 0.4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,.8)',
                    padding: 10,
                    intersect: false,
                    mode: 'index',
                    titleFont: { size: 12, family: 'Inter' },
                    bodyFont: { size: 11, family: 'Inter' },
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { size: 9, family: 'Inter' },
                        maxTicksLimit: 10,
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0,0,0,.04)' },
                    ticks: {
                        font: { size: 10, family: 'Inter' },
                        stepSize: 1,
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'nearest',
            },
            animation: { duration: 1200 }
        }
    });
}
