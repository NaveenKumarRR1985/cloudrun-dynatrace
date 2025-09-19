// Global variables for enhanced charts
let performanceChart, resourceChart, appPerformanceChart, networkChart;
let systemHistory = [];
let maxHistoryPoints = 50;

// Initialize enhanced dashboard
function initializeEnhancedDashboard() {
    setupEnhancedPerformanceChart();
    setupEnhancedResourceChart();
    setupAppPerformanceChart();
    setupNetworkChart();
    updateEnhancedDashboard();
}

// Setup enhanced performance chart with more metrics
function setupEnhancedPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    // Create gradients for a more attractive look
    const cpuGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    cpuGradient.addColorStop(0, 'rgba(13, 110, 253, 0.4)');
    cpuGradient.addColorStop(1, 'rgba(13, 110, 253, 0.05)');

    const memoryGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    memoryGradient.addColorStop(0, 'rgba(25, 135, 84, 0.4)');
    memoryGradient.addColorStop(1, 'rgba(25, 135, 84, 0.05)');

    const diskGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    diskGradient.addColorStop(0, 'rgba(255, 193, 7, 0.4)');
    diskGradient.addColorStop(1, 'rgba(255, 193, 7, 0.05)');

    const appMemoryGradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    appMemoryGradient.addColorStop(0, 'rgba(220, 53, 69, 0.4)');
    appMemoryGradient.addColorStop(1, 'rgba(220, 53, 69, 0.05)');

    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'CPU %',
                data: [],
                borderColor: 'rgb(13, 110, 253)',
                backgroundColor: cpuGradient,
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                fill: true
            }, {
                label: 'Memory %',
                data: [],
                borderColor: 'rgb(25, 135, 84)',
                backgroundColor: memoryGradient,
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                fill: true
            }, {
                label: 'Disk %',
                data: [],
                borderColor: 'rgb(255, 193, 7)',
                backgroundColor: diskGradient,
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                fill: false
            }, {
                label: 'App Memory (MB)',
                data: [],
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: appMemoryGradient,
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                fill: false,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            animation: {
                duration: 500,
                easing: 'easeOutCubic'
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)',
                        color: '#6c757d',
                        font: {
                            family: 'Segoe UI',
                            size: 12,
                            weight: '500'
                        }
                    },
                    grid: {
                        display: true,
                        drawBorder: false,
                        color: 'rgba(0, 0, 0, 0.05)',
                        lineWidth: 1
                    },
                    ticks: {
                        color: '#6c757d',
                        font: {
                            family: 'Segoe UI',
                            size: 11
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Memory (MB)',
                        color: '#6c757d',
                        font: {
                            family: 'Segoe UI',
                            size: 12,
                            weight: '500'
                        }
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#6c757d',
                        font: {
                            family: 'Segoe UI',
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6c757d',
                        font: {
                            family: 'Segoe UI',
                            size: 11
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        boxHeight: 12,
                        usePointStyle: true,
                        color: '#495057',
                        font: {
                            family: 'Segoe UI',
                            size: 12,
                            weight: '500'
                        },
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    titleFont: {
                        family: 'Segoe UI',
                        size: 13,
                        weight: '600'
                    },
                    bodyFont: {
                        family: 'Segoe UI',
                        size: 12
                    }
                }
            }
        }
    });
}

// Setup enhanced resource chart (pie chart)
function setupEnhancedResourceChart() {
    const ctx = document.getElementById('resourceChart');
    if (!ctx) return;

    resourceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['CPU Usage', 'Memory Usage', 'Disk Usage', 'Available'],
            datasets: [{
                data: [0, 0, 0, 100],
                backgroundColor: [
                    'rgb(13, 110, 253)',
                    'rgb(25, 135, 84)',
                    'rgb(255, 193, 7)',
                    'rgb(233, 236, 239)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    display: false
                }
            }
        }
    });
}

// Setup application performance chart
function setupAppPerformanceChart() {
    const ctx = document.getElementById('appPerformanceChart');
    if (!ctx) return;

    appPerformanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'App CPU %',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Active Connections',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.4,
                fill: false,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'CPU (%)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Connections'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

// Setup network chart
function setupNetworkChart() {
    const ctx = document.getElementById('networkChart');
    if (!ctx) return;

    networkChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Bytes Sent',
                data: [],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Bytes Received',
                data: [],
                borderColor: 'rgb(153, 102, 255)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Bytes'
                    }
                }
            }
        }
    });
}

// Generate traffic to increase request count
async function generateTraffic(count = 25) {
    const button = event.target;
    const originalText = button.innerHTML;
    
    button.innerHTML = '<span class="loading-spinner"></span> Generating Traffic...';
    button.disabled = true;
    
    try {
        showToast(`Firing ${count} requests...`, 'info');
        
        const promises = [];
        for (let i = 0; i < count; i++) {
            // Hit different endpoints to generate real traffic
            promises.push(fetch('/api/health').catch(() => {}));
            if (i % 5 === 0) promises.push(fetch('/api/metrics').catch(() => {}));
            if (i % 10 === 0) promises.push(fetch('/api/users').catch(() => {}));
        }
        
        await Promise.all(promises);
        
        showToast(`${count} requests completed!`, 'success');
        
        // Force immediate metrics refresh
        setTimeout(updateEnhancedDashboard, 500);
        
    } catch (error) {
        showToast('Error generating traffic', 'error');
        console.error('Traffic generation error:', error);
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Enhanced dashboard update function
async function updateEnhancedDashboard() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        console.log('Dashboard data received:', data); // Debug log
        
        // Update enhanced metric cards
        updateEnhancedMetricCards(data);
        
        // Update system information
        updateSystemInformation(data);
        
        // Store history for charts
        storeSystemHistory(data);
        
        // Update all charts
        updateAllCharts(data);
        
        // Update status
        const statusBadge = document.getElementById('status-badge');
        if (statusBadge) {
            statusBadge.innerHTML = '<i class="bi bi-check-circle"></i> System Healthy';
            statusBadge.className = 'badge bg-success fs-6';
        }
        
    } catch (error) {
        console.error('Error updating enhanced dashboard:', error);
        const statusBadge = document.getElementById('status-badge');
        if (statusBadge) {
            statusBadge.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Connection Error';
            statusBadge.className = 'badge bg-danger fs-6';
        }
    }
}

// Update enhanced metric cards with detailed information
function updateEnhancedMetricCards(data) {
    // CPU metrics
    const cpuUsage = document.getElementById('cpu-usage');
    const cpuDetails = document.getElementById('cpu-details');
    if (cpuUsage) cpuUsage.textContent = `${data.system.cpu_percent.toFixed(1)}%`;
    if (cpuDetails) cpuDetails.textContent = 
        `${data.system.cpu_count} cores @ ${(data.system.cpu_freq_current/1000).toFixed(1)} GHz`;
    
    // Memory metrics
    const memoryUsage = document.getElementById('memory-usage');
    const memoryDetails = document.getElementById('memory-details');
    if (memoryUsage) memoryUsage.textContent = `${data.system.memory_percent.toFixed(1)}%`;
    if (memoryDetails) memoryDetails.textContent = 
        `${data.system.memory_used_gb} / ${data.system.memory_total_gb} GB`;
    
    // Disk metrics
    const diskUsage = document.getElementById('disk-usage');
    const diskDetails = document.getElementById('disk-details');
    if (diskUsage) diskUsage.textContent = `${data.system.disk_percent.toFixed(1)}%`;
    if (diskDetails) diskDetails.textContent = 
        `${data.system.disk_used_gb} / ${data.system.disk_total_gb} GB`;
    
    // Network metrics
    const networkUsage = document.getElementById('network-usage');
    const networkDetails = document.getElementById('network-details');
    if (networkUsage && networkDetails) {
        const networkMB = (data.system.network_bytes_sent + data.system.network_bytes_recv) / (1024 * 1024);
        networkUsage.textContent = `${networkMB.toFixed(1)} MB`;
        networkDetails.textContent = 
            `↑${(data.system.network_bytes_sent/(1024*1024)).toFixed(1)} ↓${(data.system.network_bytes_recv/(1024*1024)).toFixed(1)}`;
    }
    
    // User and request metrics
    const totalUsers = document.getElementById('total-users');
    const totalRequests = document.getElementById('total-requests');
    const requestsDetails = document.getElementById('requests-details');
    
    if (totalUsers) totalUsers.textContent = data.app.total_users;
    if (totalRequests) totalRequests.textContent = data.app.total_requests;
    if (requestsDetails) requestsDetails.textContent = `${data.app.threads_count} threads`;
}

// Update system information panel
function updateSystemInformation(data) {
    const hostname = document.getElementById('hostname');
    const platform = document.getElementById('platform');
    const pythonVersion = document.getElementById('python-version');
    const systemUptime = document.getElementById('system-uptime');
    const appUptime = document.getElementById('app-uptime');
    
    if (hostname) hostname.textContent = data.system.hostname;
    if (platform) platform.textContent = data.system.platform;
    if (pythonVersion) pythonVersion.textContent = `v${data.system.python_version}`;
    
    // Format uptime
    if (systemUptime) systemUptime.textContent = formatUptime(data.system.uptime_seconds);
    if (appUptime) appUptime.textContent = formatUptime(data.app.uptime_seconds);
}

// Store system history for charts
function storeSystemHistory(data) {
    const timestamp = new Date().toLocaleTimeString();
    
    const historyPoint = {
        timestamp,
        cpu: data.system.cpu_percent,
        memory: data.system.memory_percent,
        disk: data.system.disk_percent,
        app_memory: data.app.memory_usage_mb,
        app_cpu: data.app.cpu_percent || 0,
        connections: data.app.active_connections,
        network_sent: data.system.network_bytes_sent,
        network_recv: data.system.network_bytes_recv
    };
    
    systemHistory.push(historyPoint);
    
    // Keep only recent history
    if (systemHistory.length > maxHistoryPoints) {
        systemHistory.shift();
    }
}

// Update all charts with real-time data
function updateAllCharts(data) {
    // Update performance chart
    if (performanceChart && systemHistory.length > 0) {
        const labels = systemHistory.map(h => h.timestamp);
        performanceChart.data.labels = labels;
        performanceChart.data.datasets[0].data = systemHistory.map(h => h.cpu);
        performanceChart.data.datasets[1].data = systemHistory.map(h => h.memory);
        performanceChart.data.datasets[2].data = systemHistory.map(h => h.disk);
        performanceChart.data.datasets[3].data = systemHistory.map(h => h.app_memory);
        performanceChart.update('none');
    }
    
    // Update resource chart with real percentages
    if (resourceChart) {
        const total = data.system.cpu_percent + data.system.memory_percent + data.system.disk_percent;
        const available = Math.max(0, 300 - total); // Max 100% for each metric
        
        resourceChart.data.datasets[0].data = [
            data.system.cpu_percent,
            data.system.memory_percent, 
            data.system.disk_percent,
            available
        ];
        resourceChart.update();
        
        // Update resource summary
        const resourceCpu = document.getElementById('resource-cpu');
        const resourceMemory = document.getElementById('resource-memory');
        const resourceDisk = document.getElementById('resource-disk');
        
        if (resourceCpu) resourceCpu.textContent = `${data.system.cpu_percent.toFixed(1)}%`;
        if (resourceMemory) resourceMemory.textContent = `${data.system.memory_percent.toFixed(1)}%`;
        if (resourceDisk) resourceDisk.textContent = `${data.system.disk_percent.toFixed(1)}%`;
    }
    
    // Update app performance chart
    if (appPerformanceChart && systemHistory.length > 0) {
        const labels = systemHistory.map(h => h.timestamp);
        appPerformanceChart.data.labels = labels;
        appPerformanceChart.data.datasets[0].data = systemHistory.map(h => h.app_cpu);
        appPerformanceChart.data.datasets[1].data = systemHistory.map(h => h.connections);
        appPerformanceChart.update('none');
    }
    
    // Update network chart
    if (networkChart && systemHistory.length > 0) {
        const labels = systemHistory.map(h => h.timestamp);
        networkChart.data.labels = labels;
        networkChart.data.datasets[0].data = systemHistory.map(h => h.network_sent);
        networkChart.data.datasets[1].data = systemHistory.map(h => h.network_recv);
        networkChart.update('none');
    }
}

// Helper function to format uptime
function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
}

// Enhanced action functions
async function simulateWork() {
    const button = event.target;
    const originalText = button.innerHTML;
    
    button.innerHTML = '<span class="loading-spinner"></span> Working...';
    button.disabled = true;
    
    try {
        const response = await fetch('/api/simulate-work');
        const result = await response.json();
        showToast('Work simulation completed!', 'success');
    } catch (error) {
        showToast('Error simulating work', 'error');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

async function stressTest() {
    const button = event.target;
    const originalText = button.innerHTML;
    
    button.innerHTML = '<span class="loading-spinner"></span> Testing...';
    button.disabled = true;
    
    // Simulate CPU stress by running multiple work simulations
    try {
        const promises = [];
        for (let i = 0; i < 5; i++) {
            promises.push(fetch('/api/simulate-work'));
        }
        await Promise.all(promises);
        showToast('CPU stress test completed!', 'warning');
    } catch (error) {
        showToast('Stress test failed', 'error');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

async function memoryTest() {
    showToast('Memory usage will increase temporarily', 'info');
    // Create some temporary data to increase memory usage
    const tempData = new Array(100000).fill('test data for memory usage simulation');
    setTimeout(() => {
        tempData.length = 0; // Clear the array
        showToast('Memory test completed', 'success');
    }, 3000);
}

function refreshMetrics() {
    updateEnhancedDashboard();
    showToast('All metrics refreshed!', 'info');
}

function clearData() {
    systemHistory.length = 0;
    if (performanceChart) {
        performanceChart.data.labels = [];
        performanceChart.data.datasets.forEach(dataset => dataset.data = []);
        performanceChart.update();
    }
    if (appPerformanceChart) {
        appPerformanceChart.data.labels = [];
        appPerformanceChart.data.datasets.forEach(dataset => dataset.data = []);
        appPerformanceChart.update();
    }
    if (networkChart) {
        networkChart.data.labels = [];
        networkChart.data.datasets.forEach(dataset => dataset.data = []);
        networkChart.update();
    }
    showToast('Chart data cleared!', 'info');
}

function updateChartTimeRange() {
    // Adjust history points based on time range
    switch(timeRange) {
        case '1m':
            maxHistoryPoints = 20;
            break;
        case '5m':
            maxHistoryPoints = 50;
            break;
        case '15m':
            maxHistoryPoints = 150;
            break;
    }
    
    // Trim history if needed
    if (systemHistory.length > maxHistoryPoints) {
        systemHistory = systemHistory.slice(-maxHistoryPoints);
    }
    
    showToast(`Time range set to ${timeRange}`, 'info');
}

// Toast notification function
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}
