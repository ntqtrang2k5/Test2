/* ============================================
   KHACH HANG MODULE JAVASCRIPT
   ============================================ */

// --- RENDER CUSTOMERS ---
function renderCustomers() {
    // Lưu ý: Trong bản Django, phần này sẽ được render trực tiếp từ server (Server-side rendering)
    // Nhưng tui vẫn giữ logic JS nếu ông muốn làm các hiệu ứng hoặc xử lý tại chỗ.
    console.log("Dữ liệu khách hàng đã được load từ Django");
}

// --- CUSTOMER MODAL ---
function openCustomerModal(mode, id, name, phone, cccd) {
    const modal = document.getElementById('modal-customer');
    const title = document.getElementById('modal-kh-title');
    const historyArea = document.getElementById('modal-kh-history');

    if (!modal || !title) return;

    if (mode === 'add') {
        title.innerText = 'Thêm khách hàng mới';
        if (historyArea) historyArea.classList.remove('active');

        const nextId = document.getElementById('btn-add-customer')?.dataset.nextId || 'KH001';
        document.getElementById('inp-kh-id').value = nextId;
        document.getElementById('inp-kh-name').value = '';
        document.getElementById('inp-kh-phone').value = '';
        document.getElementById('inp-kh-cmnd').value = '';
    } else {
        title.innerText = 'Thông tin chi tiết: ' + name;
        if (historyArea) historyArea.classList.add('active');

        document.getElementById('inp-kh-id').value = id || '';
        document.getElementById('inp-kh-name').value = name || '';
        document.getElementById('inp-kh-phone').value = phone || '';
        document.getElementById('inp-kh-cmnd').value = cccd || '';
    }

    modal.classList.add('active');
}

function closeCustomerModal() {
    const modal = document.getElementById('modal-customer');
    if (modal) modal.classList.remove('active');
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

async function saveCustomerData() {
    const id = document.getElementById('inp-kh-id')?.value;
    const name = document.getElementById('inp-kh-name')?.value.trim();
    const phone = document.getElementById('inp-kh-phone')?.value.trim();
    const cccd = document.getElementById('inp-kh-cmnd')?.value.trim();

    // 2a. Validation Tên Khách Hàng
    const nameRegex = /^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸửữựỳỵỷỹýỹ\s]+$/;
    if (!name || !nameRegex.test(name)) {
        alert('Tên khách hàng không hợp lệ (không được chứa số hoặc ký tự đặc biệt)');
        return;
    }

    // 3a. Validation Số Điện Thoại
    const phoneRegex = /^0\d{9}$/;
    if (!phoneRegex.test(phone)) {
        alert('SĐT không hợp lệ (phải có 10 số và bắt đầu bằng số 0)');
        return;
    }

    // 4a. Validation CCCD
    const cccdRegex = /^\d{12}$/;
    if (!cccdRegex.test(cccd)) {
        alert('CCCD không hợp lệ (phải có đúng 12 số)');
        return;
    }

    try {
        const response = await fetch('/khach-hang/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ id, name, phone, cccd })
        });
        
        const result = await response.json();
        if (result.success) {
            alert(result.message);
            window.location.reload();
        } else {
            alert('Lỗi: ' + result.message);
        }
    } catch (error) {
        console.error('Error saving customer:', error);
        alert('Có lỗi xảy ra khi lưu dữ liệu!');
    }
}

async function deleteCustomer(id) {
    if (confirm('Bạn có chắc chắn muốn xóa khách hàng ' + id + '?')) {
        try {
            const response = await fetch('/khach-hang/delete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ id })
            });

            const result = await response.json();
            if (result.success) {
                alert(result.message);
                window.location.reload();
            } else {
                alert('Lỗi: ' + result.message);
            }
        } catch (error) {
            console.error('Error deleting customer:', error);
            alert('Có lỗi xảy ra khi xóa dữ liệu!');
        }
    }
}

// --- UTILS ---
function removeAccents(str) {
    if (!str) return "";
    return str.normalize('NFD')
              .replace(/[\u0300-\u036f]/g, '')
              .replace(/đ/g, 'd').replace(/Đ/g, 'D');
}

// --- SEARCH FUNCTION ---
function applyCustomerFilters() {
    const searchInput = document.querySelector('.kh-search-input');
    if (!searchInput) return;
    
    // Bỏ dấu và đưa về chữ thường cả từ khóa tìm kiếm
    const query = removeAccents(searchInput.value.toLowerCase().trim());
    const cards = document.querySelectorAll('.customer-card');
    
    cards.forEach(card => {
        // Bỏ dấu và đưa về chữ thường tất cả các thông tin cần search
        const name = removeAccents(card.querySelector('.customer-name')?.textContent.toLowerCase() || '');
        const id = removeAccents(card.querySelector('.customer-id')?.textContent.toLowerCase() || '');
        const phone = removeAccents(card.querySelector('.customer-info-list')?.textContent.toLowerCase() || '');
        
        if (name.includes(query) || id.includes(query) || phone.includes(query)) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.kh-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            applyCustomerFilters();
        });
    }

    // Add Input Masks for Customer Modal
    const nameInp = document.getElementById('inp-kh-name');
    if (nameInp) {
        nameInp.oninput = (e) => {
            let v = e.target.value.replace(/[^a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸửữựỳỵỷỹýỹ\s]/g, '');
            e.target.value = v;
        };
    }

    const phoneInp = document.getElementById('inp-kh-phone');
    if (phoneInp) {
        phoneInp.oninput = (e) => {
            let v = e.target.value.replace(/[^\d]/g, '');
            if (v.length > 10) v = v.slice(0, 10);
            e.target.value = v;
        };
    }

    const cccdInp = document.getElementById('inp-kh-cmnd');
    if (cccdInp) {
        cccdInp.oninput = (e) => {
            let v = e.target.value.replace(/[^\d]/g, '');
            if (v.length > 12) v = v.slice(0, 12);
            e.target.value = v;
        };
    }
});
