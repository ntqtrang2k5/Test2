/**
 * Common JS for Car Rent Project
 * Version: 2.0
 */

console.log('Common JS loaded (V2.0)');

const FORMATTER = new Intl.NumberFormat('vi-VN');

function formatCurrency(value) {
    if (!value && value !== 0) return "0";
    return FORMATTER.format(value);
}

function parseCurrency(str) {
    if (!str) return 0;
    return parseInt(str.toString().replace(/[^\d]/g, '')) || 0;
}

// Global Tab switcher
function switchTab(e, tabId) {
    console.log('Global switchTab called:', tabId);
    document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    if (e && e.currentTarget) e.currentTarget.classList.add('active');
    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.add('active');
    }
}

// Global Picker opener
function openPicker(type) {
    console.log('Global openPicker called:', type);
    if (type === 'start' && window.fpStart) window.fpStart.open();
    else if (type === 'end' && window.fpEnd) window.fpEnd.open();
    else {
        // Fallback: try to find by ID if window globals aren't set
        const el = document.getElementById(type === 'start' ? 'd-start-date' : 'd-end-date');
        if (el && el._flatpickr) el._flatpickr.open();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Common JS: DOMContentLoaded');
});
