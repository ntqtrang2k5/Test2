/* ============================================
   QUAN LY XE MODULE JAVASCRIPT
   ============================================ */

let currentConfigTab = 'country';
let currentConfigEditId = null;

// --- TAB SWITCHING ---
function switchCarManagementTab(tabId, element) {
    document.querySelectorAll('.ql-tab').forEach(tab => tab.classList.remove('active'));
    if (element) element.classList.add('active');

    document.querySelectorAll('.car-management-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    let targetId = 'car-details-content';
    if (tabId === 'config') targetId = 'config-content';
    
    const targetContent = document.getElementById(targetId);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

function switchConfigSubTab(tabId, element) {
    currentConfigTab = tabId;
    document.querySelectorAll('.config-sub-tab').forEach(tab => tab.classList.remove('active'));
    if (element) element.classList.add('active');
    
    // Hide all tables
    document.querySelectorAll('.config-table').forEach(table => {
        table.style.display = 'none';
        table.classList.remove('active');
    });
    
    // Show target table
    const targetTable = document.getElementById(`config-table-${tabId}`);
    if (targetTable) {
        targetTable.style.display = 'table';
        targetTable.classList.add('active');
    }

    // Reset search input when switching tabs
    const searchInput = document.getElementById('config-search-input');
    if (searchInput) {
        searchInput.value = '';
        filterConfigTable();
    }
}

// --- MODAL CONTROL ---

function openConfigModal(tabId = null, editId = null) {
    if (tabId) currentConfigTab = tabId;
    currentConfigEditId = editId;

    const modalId = `modal-config-${currentConfigTab}`;
    const modal = document.getElementById(modalId);
    if (!modal) {
        console.error('Modal not found:', modalId);
        return;
    }

    // Reset Form
    const form = modal.querySelector('form');
    if (form) form.reset();

    // Set Title
    const titleObj = {
        'country': 'Quốc gia',
        'brand': 'Hãng xe',
        'style': 'Kiểu xe',
        'color': 'Màu sơn',
        'model': 'Loại xe'
    };
    const titleEl = document.getElementById(`title-config-${currentConfigTab}`);
    if (titleEl) {
        titleEl.textContent = (editId ? 'Sửa' : 'Thêm') + ' cấu hình ' + titleObj[currentConfigTab];
    }

    // Populate Dropdowns
    populateConfigDropdowns();

    // Populate Data for Edit
    if (editId) {
        fillEditData(currentConfigTab, editId);
    }

    // Use common openModal function
    if (typeof openModal === 'function') {
        openModal(modalId);
    } else {
        modal.classList.add('active');
    }
}

function populateConfigDropdowns() {
    // Populate Countries in Brand modal
    const brandCountrySelect = document.getElementById('input-brand-country');
    if (brandCountrySelect && typeof G_COUNTRIES !== 'undefined') {
        brandCountrySelect.innerHTML = '<option value="">-- Chọn Quốc gia --</option>' + 
            G_COUNTRIES.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    }

    // Populate Brands in Model modal
    const modelBrandSelect = document.getElementById('input-model-brand');
    if (modelBrandSelect && typeof G_BRANDS !== 'undefined') {
        modelBrandSelect.innerHTML = '<option value="">-- Chọn Hãng xe --</option>' + 
            G_BRANDS.map(b => `<option value="${b.id}">${b.name}</option>`).join('');
    }

    // Populate Styles in Model modal
    const modelStyleSelect = document.getElementById('input-model-style');
    if (modelStyleSelect && typeof G_STYLES !== 'undefined') {
        modelStyleSelect.innerHTML = '<option value="">-- Chọn Kiểu xe --</option>' + 
            G_STYLES.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    }
}

function fillEditData(tab, id) {
    if (tab === 'country') {
        const item = G_COUNTRIES.find(i => i.id === id);
        if (item) document.getElementById('input-country-name').value = item.name;
    } else if (tab === 'brand') {
        const item = G_BRANDS.find(i => i.id === id);
        if (item) {
            document.getElementById('input-brand-name').value = item.name;
            document.getElementById('input-brand-country').value = item.countryId;
        }
    } else if (tab === 'style') {
        const item = G_STYLES.find(i => i.id === id);
        if (item) document.getElementById('input-style-name').value = item.name;
    } else if (tab === 'color') {
        // Find in table directly if list not global
        const table = document.getElementById('config-table-color');
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const editBtn = row.querySelector('[onclick*="'+id+'"]');
            if (editBtn) {
                const name = row.cells[1].textContent.trim();
                document.getElementById('input-color-name').value = name;
            }
        });
    } else if (tab === 'model') {
        const item = G_MODELS.find(i => i.id === id);
        if (item) {
            document.getElementById('input-model-name').value = item.name;
            document.getElementById('input-model-brand').value = item.brandId;
            document.getElementById('input-model-style').value = item.styleId;
            document.getElementById('input-model-seats').value = item.seats;
        }
    }
}

function saveConfigSpecific(e, type) {
    if (e) e.preventDefault();

    let payload = {
        type: type,
        id: currentConfigEditId || ''
    };

    if (type === 'country') {
        payload.name = document.getElementById('input-country-name').value.trim();
    } else if (type === 'brand') {
        payload.name = document.getElementById('input-brand-name').value.trim();
        payload.countryId = document.getElementById('input-brand-country').value;
    } else if (type === 'style') {
        payload.name = document.getElementById('input-style-name').value.trim();
    } else if (type === 'color') {
        payload.name = document.getElementById('input-color-name').value.trim();
    } else if (type === 'model') {
        payload.name = document.getElementById('input-model-name').value.trim();
        payload.brandId = document.getElementById('input-model-brand').value;
        payload.styleId = document.getElementById('input-model-style').value;
        payload.seats = document.getElementById('input-model-seats').value;
    }

    // Basic Validation
    if (!payload.name) {
        alert('Vui lòng nhập tên!');
        return;
    }
    if (type === 'brand' && !payload.countryId) {
        alert('Vui lòng chọn quốc gia!');
        return;
    }
    if (type === 'model') {
        if (!payload.brandId || !payload.styleId || !payload.seats) {
            alert('Vui lòng điền đủ hãng xe, kiểu xe và số chỗ!');
            return;
        }
    }

    fetch(CONFIG_API_URL.SAVE, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            closeModal(`modal-config-${type}`);
            window.location.reload();
        } else {
            alert(data.error || 'Có lỗi xảy ra');
        }
    })
    .catch(err => {
        console.error('Save Error:', err);
        alert('Lỗi kết nối Server!');
    });
}

function deleteConfigItem(tabId, deleteId) {
    if (!confirm(`Bạn có chắc chắn muốn xóa không?`)) return;

    fetch(CONFIG_API_URL.DELETE, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify({ type: tabId, id: deleteId })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert(data.error || 'Có lỗi xảy ra khi xóa!');
        }
    })
    .catch(err => {
        console.error('Delete Error:', err);
        alert('Lỗi kết nối Server!');
    });
}

function filterConfigTable() {
    const input = document.getElementById('config-search-input');
    if (!input) return;
    const searchVal = removeAccents(input.value);
    
    const table = document.querySelector('.config-table.active');
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        if (row.cells.length < 2) return; // Skip "No data" row
        
        // Search in all columns except the last one (Actions)
        let rowContent = "";
        for(let i=0; i < row.cells.length - 1; i++) {
            rowContent += row.cells[i].textContent + " ";
        }
        
        if (removeAccents(rowContent).includes(searchVal)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Quan Ly Xe JS Initialized');
});
