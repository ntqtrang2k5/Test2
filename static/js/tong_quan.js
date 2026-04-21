/* ============================================
   TONG QUAN MODULE JAVASCRIPT
   Combined with Lich Xe and Tai Chinh
   ============================================ */

// --- GLOBAL DATA FOR MODULES ---
let currentScheduleDate = new Date(); 

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    
    // Initial render if schedule tab is active
    const activeTab = document.querySelector('.tab-item.active');
    if (activeTab && activeTab.getAttribute('data-tab') === 'schedule') {
        renderVehicleSchedule();
    }
    
    // Schedule Event Listeners
    document.getElementById('prev-month')?.addEventListener('click', () => changeScheduleMonth(-1));
    document.getElementById('next-month')?.addEventListener('click', () => changeScheduleMonth(1));

    // Finance Event Listeners
    document.querySelector('.finance-btn-filter')?.addEventListener('click', filterFinanceTable);
    document.querySelector('.finance-btn-reset')?.addEventListener('click', resetFinanceFilters);

    console.log('Dashboard Data-Driven JS loaded');
});

// --- FINANCE FILTER LOGIC ---
function filterFinanceTable() {
    const type = document.getElementById('finance-type-select')?.value || "all";
    const timeFrame = document.getElementById('finance-time-select')?.value || "all";
    const rows = document.querySelectorAll('.finance-row');

    // Reference today from server or system
    const today = window.serverToday ? new Date(window.serverToday) : new Date();
    today.setHours(0,0,0,0);
    
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    let totalIncome = 0;
    let totalExpense = 0;

    rows.forEach(row => {
        const rowType = row.getAttribute('data-type');
        const dateStr = row.querySelector('.col-date').innerText.trim(); // dd/mm/yyyy

        const matchesType = type === 'all' || type === rowType;
        
        let matchesTime = true;
        if (timeFrame !== 'all') {
            const [d, m, y] = dateStr.split('/').map(Number);
            const rowDate = new Date(y, m - 1, d);
            rowDate.setHours(0,0,0,0);

            if (timeFrame === 'today') {
                matchesTime = rowDate.getTime() === today.getTime();
            } else if (timeFrame === 'yesterday') {
                matchesTime = rowDate.getTime() === yesterday.getTime();
            } else if (timeFrame === 'this_month') {
                matchesTime = rowDate.getFullYear() === today.getFullYear() && rowDate.getMonth() === today.getMonth();
            }
        }

        if (matchesType && matchesTime) {
            row.style.display = '';
            
            // Recalculate totals from visible rows
            const incomeDiv = row.querySelector('.cell-income');
            const expenseDiv = row.querySelector('.cell-expense');
            if (incomeDiv) totalIncome += parseInt(incomeDiv.innerText.replace(/[^\d]/g, '')) || 0;
            if (expenseDiv) totalExpense += parseInt(expenseDiv.innerText.replace(/[^\d]/g, '')) || 0;
        } else {
            row.style.display = 'none';
        }
    });

    // Update the 3 summary cards at the top
    const sumIncome = document.getElementById('summary-income');
    const sumExpense = document.getElementById('summary-expense');
    const sumProfit = document.getElementById('summary-profit');

    if (sumIncome)  sumIncome.innerText  = formatCurrency(totalIncome) + " đ";
    if (sumExpense) sumExpense.innerText = formatCurrency(totalExpense) + " đ";
    if (sumProfit)  sumProfit.innerText  = formatCurrency(totalIncome - totalExpense) + " đ";
}

function resetFinanceFilters() {
    const typeSelect = document.getElementById('finance-type-select');
    const timeSelect = document.getElementById('finance-time-select');
    if (typeSelect) typeSelect.value = 'all';
    if (timeSelect) timeSelect.value = 'all';
    filterFinanceTable();
}

// Update data from window globals if they change
function getSchedulerData() { return window.schedulerData || []; }
function getCarsData() { return window.carsData || []; }

// --- TAB SYSTEM LOGIC ---
function initTabs() {
    const tabItems = document.querySelectorAll('.tab-item');
    tabItems.forEach(item => {
        item.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            tabItems.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            const targetContent = document.getElementById('tab-' + tabId);
            if (targetContent) targetContent.classList.add('active');

            if (tabId === 'schedule') {
                renderVehicleSchedule();
            }
        });
    });
}

// --- VEHICLE SCHEDULE LOGIC ---
function renderVehicleSchedule() {
    const gridContainer = document.getElementById('fleet-scheduler-grid');
    const monthTitle = document.getElementById('current-schedule-month');
    if (!gridContainer || !monthTitle) return;

    // Use latest data from globals
    const vehicleBookings = getSchedulerData();
    const cars = getCarsData();
    const year = currentScheduleDate.getFullYear();
    const month = currentScheduleDate.getMonth();
    const monthNames = ["Tháng 01", "Tháng 02", "Tháng 03", "Tháng 04", "Tháng 05", "Tháng 06", "Tháng 07", "Tháng 08", "Tháng 09", "Tháng 10", "Tháng 11", "Tháng 12"];
    monthTitle.textContent = `${monthNames[month]} / ${year}`;

    const daysInMonth = new Date(year, month + 1, 0).getDate();
    // Use server date if available, fallback to client date
    const today = window.serverToday ? new Date(window.serverToday) : new Date();
    const isCurrentMonth = today.getFullYear() === year && today.getMonth() === month;

    let tableHtml = `<div class="scheduler-table">`;
    tableHtml += `<div class="scheduler-header-row">
                    <div class="car-col-header">Phương tiện</div>`;
    for (let d = 1; d <= daysInMonth; d++) {
        const dateObj = new Date(year, month, d);
        const dayName = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"][dateObj.getDay()];
        const todayClass = (isCurrentMonth && d === today.getDate()) ? 'today' : '';
        tableHtml += `<div class="day-col-header ${todayClass}">${dayName}<span>${d}</span></div>`;
    }
    tableHtml += `</div>`;

    // Use Real Cars Data from Django
    // cars is already defined above via getCarsData()

    cars.forEach(car => {
        tableHtml += `<div class="scheduler-row">
                        <div class="car-col-label">
                            <div class="row-car-name">${car.name}</div>
                            <div class="row-car-plate">${car.plate}</div>
                        </div>
                        <div class="day-cells-container">`;
        
        for (let d = 1; d <= daysInMonth; d++) {
            const todayClass = (isCurrentMonth && d === today.getDate()) ? 'today' : '';
            tableHtml += `<div class="grid-cell ${todayClass}"></div>`;
        }

        // Use Real Bookings from Django
        const carBookings = vehicleBookings.filter(b => b.carId === car.id);
        const startOfMonth = new Date(year, month, 1, 0, 0, 0);
        const endOfMonth = new Date(year, month, daysInMonth, 23, 59, 59);
        const totalMs = endOfMonth - startOfMonth;

        carBookings.forEach(booking => {
            const bStart = new Date(booking.start);
            const bEnd = new Date(booking.end);

            if (bStart <= endOfMonth && bEnd >= startOfMonth) {
                const effectiveStart = Math.max(startOfMonth, bStart);
                const effectiveEnd = Math.min(endOfMonth, bEnd);
                
                const leftPercent = ((effectiveStart - startOfMonth) / totalMs) * 100;
                const widthPercent = ((effectiveEnd - effectiveStart) / totalMs) * 100;

                tableHtml += `<div class="event-bar ${booking.status}" 
                                   style="left: ${leftPercent}%; width: ${widthPercent}%;" 
                                   title="${booking.title}">
                                   <span class="event-title" style="font-size: 10px; line-height: 20px; padding-left: 5px;">${booking.title}</span>
                              </div>`;
            }
        });
        tableHtml += `</div></div>`;
    });

    tableHtml += `</div>`;
    gridContainer.innerHTML = tableHtml;

    // Check if we should disable the Prev button
    const prevBtn = document.getElementById('prev-month');
    if (prevBtn) {
        const limitDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
        const currentDateFirst = new Date(year, month, 1);
        if (currentDateFirst <= limitDate) {
            prevBtn.disabled = true;
            prevBtn.style.opacity = '0.3';
            prevBtn.style.cursor = 'not-allowed';
        } else {
            prevBtn.disabled = false;
            prevBtn.style.opacity = '1';
            prevBtn.style.cursor = 'pointer';
        }
    }
}

function changeScheduleMonth(offset) {
    const nextDate = new Date(currentScheduleDate);
    nextDate.setMonth(nextDate.getMonth() + offset);
    
    // Safety check again using server date
    const today = window.serverToday ? new Date(window.serverToday) : new Date();
    const limitDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const nextDateFirst = new Date(nextDate.getFullYear(), nextDate.getMonth(), 1);
    
    if (offset < 0 && nextDateFirst < limitDate) return;

    currentScheduleDate = nextDate;
    renderVehicleSchedule();
}

function formatCurrency(v) {
    return new Intl.NumberFormat('vi-VN').format(v);
}
