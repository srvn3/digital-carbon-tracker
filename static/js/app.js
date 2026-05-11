const themeToggle = document.querySelector('#theme-toggle');
const body = document.body;
const notifyPermission = window.Notification && Notification.permission;

function setTheme(theme) {
    body.dataset.theme = theme;
    localStorage.setItem('carbonTheme', theme);
    if (theme === 'dark') {
        body.classList.add('dark-mode');
    } else {
        body.classList.remove('dark-mode');
    }
}

function initTheme() {
    const storedTheme = localStorage.getItem('carbonTheme') || 'dark';
    setTheme(storedTheme);
    if (themeToggle) themeToggle.checked = storedTheme === 'dark';
}

function showNotification(title, message) {
    if (!('Notification' in window)) return;
    if (Notification.permission === 'granted') {
        new Notification(title, { body: message });
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification(title, { body: message });
            }
        });
    }
}

function initForms() {
    const registerForm = document.querySelector('#register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', e => {
            const email = document.querySelector('#register-email').value;
            const password = document.querySelector('#register-password').value;
            const confirm = document.querySelector('#register-confirm-password').value;
            const emailRegex = /^[\w.-]+@[\w.-]+\.\w+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address.');
                return;
            }
            if (password.length < 8) {
                e.preventDefault();
                alert('Password must be at least 8 characters.');
                return;
            }
            if (password !== confirm) {
                e.preventDefault();
                alert('Passwords do not match.');
            }
        });
    }

    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        const emailInput = document.querySelector('#email');
        const rememberCheckbox = document.querySelector('#remember-me');
        const savedEmailsList = document.querySelector('#saved-emails');
        const storageKey = 'carbonTracker_savedEmails';
        const savedEmails = JSON.parse(localStorage.getItem(storageKey) || '[]');

        function renderSavedEmails() {
            if (!savedEmailsList) return;
            savedEmailsList.innerHTML = savedEmails.map(email => `<option value="${email}"></option>`).join('');
        }

        renderSavedEmails();

        if (emailInput && !emailInput.value && savedEmails.length) {
            emailInput.value = savedEmails[0];
        }

        loginForm.addEventListener('submit', () => {
            const emailValue = emailInput?.value.trim().toLowerCase();
            if (!emailValue || !rememberCheckbox?.checked) return;
            if (!savedEmails.includes(emailValue)) {
                savedEmails.unshift(emailValue);
                if (savedEmails.length > 8) savedEmails.splice(8);
                localStorage.setItem(storageKey, JSON.stringify(savedEmails));
                renderSavedEmails();
            }
        });
    }

    const usageForm = document.querySelector('#usage-form');
    if (usageForm) {
        usageForm.addEventListener('submit', async e => {
            e.preventDefault();
            const formData = new FormData(usageForm);
            try {
                const response = await fetch('/submit-usage', {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) {
                    let errorText = await response.text();
                    try {
                        const jsonError = JSON.parse(errorText);
                        errorText = jsonError.message || errorText;
                    } catch (parseError) {
                        // leave raw text if not JSON
                    }
                    showStatus(`Submission failed: ${response.status} ${response.statusText} - ${errorText}`, 'danger');
                    console.error('Usage submit failed:', response.status, response.statusText, errorText);
                    return;
                }
                const data = await response.json();
                if (data.status === 'success') {
                    displaySummary(data);
                    if (Array.isArray(data.notifications) && data.notifications.length) {
                        data.notifications.forEach(msg => showNotification('Usage Alert', msg));
                    }
                    showStatus(data.message || 'Usage logged and charts updated successfully.', 'success');
                } else {
                    showStatus(data.message || 'Unable to submit usage data. Please login again.', 'danger');
                }
            } catch (error) {
                console.error('Submit usage error:', error);
                showStatus('Unable to submit usage data. Check console for details.', 'danger');
            }
        });
    }
}

function displaySummary(data) {
    const todayTotal = document.querySelector('#today-total');
    if (todayTotal) todayTotal.textContent = `${data.total_co2} g`; 
    const weeklyTotal = document.querySelector('#weekly-total');
    if (weeklyTotal) weeklyTotal.textContent = `${data.weekly_total} g`;
    const monthlyTotal = document.querySelector('#monthly-total');
    if (monthlyTotal) monthlyTotal.textContent = `${data.monthly_total} g`;
    const greenScore = document.querySelector('#green-score');
    if (greenScore) greenScore.textContent = `${data.green_score}`;
    const ecoTip = document.querySelector('#eco-tip');
    if (ecoTip && data.eco_tip) ecoTip.textContent = data.eco_tip;
    updateCharts(data.contributions);
    // Reload the page to update all charts with fresh data from server
    window.location.reload();
}

function showStatus(message, type = 'info') {
    const statusBox = document.querySelector('#status-box');
    if (!statusBox) return;
    statusBox.textContent = message;
    statusBox.className = `status-message ${type}`;
    setTimeout(() => {
        statusBox.classList.remove('show');
    }, 5500);
    statusBox.classList.add('show');
}

let pieChart = null;
let barChart = null;
let lineChart = null;

function initCharts(chartData) {
    const pieCanvas = document.querySelector('#carbon-pie');
    const barCanvas = document.querySelector('#weekly-bar');
    const lineCanvas = document.querySelector('#monthly-line');
    const labels = chartData.labels.length ? chartData.labels : ['Instagram', 'WhatsApp', 'YouTube', 'Netflix', 'Gmail', 'Drive', 'Spotify', 'Zoom'];
    const values = chartData.values.length ? chartData.values : [20, 10, 15, 12, 8, 5, 18, 12];
    const weeklyLabels = chartData.weeklyLabels.length ? chartData.weeklyLabels : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const weeklyValues = chartData.weeklyValues.length ? chartData.weeklyValues : [120, 180, 140, 160, 125, 90, 200];
    const monthlyLabels = chartData.monthlyLabels.length ? chartData.monthlyLabels : ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
    const monthlyValues = chartData.monthlyValues.length ? chartData.monthlyValues : [600, 520, 580, 610];

    if (pieCanvas) {
        pieChart = new Chart(pieCanvas, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    label: 'Carbon Contribution',
                    data: values,
                    borderColor: '#0f172a',
                    borderWidth: 2,
                    backgroundColor: ['#5dd39e', '#14b8a6', '#38bdf8', '#a78bfa', '#f97316', '#0ea5e9', '#22c55e', '#facc15']
                }]
            },
            options: {
                responsive: true,
                animation: { duration: 900, easing: 'easeOutQuart' },
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#dbeafe' } },
                    tooltip: { callbacks: { label: context => `${context.label}: ${context.formattedValue} g CO2` } }
                }
            }
        });
    }
    if (barCanvas) {
        barChart = new Chart(barCanvas, {
            type: 'bar',
            data: {
                labels: weeklyLabels,
                datasets: [{
                    label: 'Weekly CO2 emissions',
                    data: weeklyValues,
                    backgroundColor: weeklyValues.map(() => 'rgba(34, 197, 94, 0.8)'),
                    borderRadius: 12,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                animation: { duration: 900, easing: 'easeOutQuart' },
                scales: {
                    x: { ticks: { color: '#cbd5e1' }, grid: { display: false } },
                    y: { beginAtZero: true, ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(255,255,255,0.08)' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
    if (lineCanvas) {
        lineChart = new Chart(lineCanvas, {
            type: 'line',
            data: {
                labels: monthlyLabels,
                datasets: [{
                    label: 'Monthly trend',
                    data: monthlyValues,
                    borderColor: '#60a5fa',
                    backgroundColor: 'rgba(96,165,250,0.18)',
                    pointBackgroundColor: '#38bdf8',
                    tension: 0.35,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                animation: { duration: 900, easing: 'easeOutQuart' },
                scales: {
                    x: { ticks: { color: '#cbd5e1' }, grid: { display: false } },
                    y: { beginAtZero: true, ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(255,255,255,0.08)' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
}

function updateCharts(contributions) {
    if (!contributions) return;
    const labels = Object.keys(contributions).map(key => key.charAt(0).toUpperCase() + key.slice(1));
    const values = Object.values(contributions);
    if (pieChart) {
        pieChart.data.labels = labels;
        pieChart.data.datasets[0].data = values;
        pieChart.update();
    }
}

function initDashboardCharts() {
    const chartPayload = {
        labels: JSON.parse(document.querySelector('#pie-labels')?.textContent || '[]'),
        values: JSON.parse(document.querySelector('#pie-values')?.textContent || '[]'),
        weeklyLabels: JSON.parse(document.querySelector('#weekly-labels')?.textContent || '[]'),
        weeklyValues: JSON.parse(document.querySelector('#weekly-values')?.textContent || '[]'),
        monthlyLabels: JSON.parse(document.querySelector('#monthly-labels')?.textContent || '[]'),
        monthlyValues: JSON.parse(document.querySelector('#monthly-values')?.textContent || '[]')
    };
    initCharts(chartPayload);
}

function showDashboardNotifications() {
    const notificationData = JSON.parse(document.querySelector('#notifications-data')?.textContent || '[]');
    if (!notificationData.length) return;
    notificationData.forEach(alert => {
        if (alert.read_status === 0 && alert.level === 'warning') {
            showNotification('Carbon Alert', alert.message);
        }
    });
}

function initThemeToggle() {
    if (!themeToggle) return;
    themeToggle.addEventListener('change', () => {
        setTheme(themeToggle.checked ? 'dark' : 'light');
    });
}

function initDocument() {
    initTheme();
    initThemeToggle();
    initForms();
    if (document.querySelector('#carbon-pie')) {
        initDashboardCharts();
        showDashboardNotifications();
    }
}

document.addEventListener('DOMContentLoaded', initDocument);
