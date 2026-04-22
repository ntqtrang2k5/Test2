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
    
    // Activate Tab Content
    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.add('active');
    }

    // Activate Tab Item (the button)
    if (e && e.currentTarget) {
        e.currentTarget.classList.add('active');
    } else {
        // Programmatic switch: find the tab item that points to this tabId
        const items = document.querySelectorAll('.tab-item');
        items.forEach(item => {
            if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(tabId)) {
                item.classList.add('active');
            }
        });
    }

    // Update URL Hash without jumping (using history API to stay clean)
    if (window.history.pushState) {
        window.history.pushState(null, null, '#' + tabId);
    } else {
        window.location.hash = tabId;
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

function removeAccents(str) {
    if (!str) return "";
    return str.toString()
              .normalize('NFD')
              .replace(/[\u0300-\u036f]/g, '')
              .replace(/đ/g, 'd').replace(/Đ/g, 'D');
}

// Global Confirm Popup
window.showConfirm = function(message, onConfirm) {
    const modal = document.getElementById('confirm-modal-root');
    const msgEl = document.getElementById('confirm-modal-msg');
    const btnOk = document.getElementById('confirm-modal-ok');
    const btnCancel = document.getElementById('confirm-modal-cancel');

    if (!modal || !msgEl || !btnOk || !btnCancel) {
        // Fallback to native confirm if modal elements are missing
        if (confirm(message)) onConfirm();
        return;
    }

    msgEl.innerText = message || "Bạn chưa lưu thông tin, có muốn thoát?";
    modal.classList.add('active');

    // Use cloneNode to clear previous event listeners
    const newBtnOk = btnOk.cloneNode(true);
    const newBtnCancel = btnCancel.cloneNode(true);
    btnOk.parentNode.replaceChild(newBtnOk, btnOk);
    btnCancel.parentNode.replaceChild(newBtnCancel, btnCancel);

    newBtnOk.onclick = () => {
        modal.classList.remove('active');
        if (onConfirm) onConfirm();
    };

    newBtnCancel.onclick = () => {
        modal.classList.remove('active');
    };
    
    modal.onclick = (e) => {
        if (e.target === modal) modal.classList.remove('active');
    };
};

document.addEventListener('DOMContentLoaded', () => {
    console.log('Common JS: DOMContentLoaded');
});
