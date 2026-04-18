document.addEventListener('DOMContentLoaded', function() {
    initForm();

    const addForm = document.getElementById('add-car-form');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveNewCar();
        });
    }
});

function initForm() {
    // Populate dropdowns using lists from common.js
    if (typeof updateAllFormDropdowns === 'function') {
        updateAllFormDropdowns('add');
    }
}

function saveNewCar() {
    const carData = {
        name: document.getElementById('add-car-name').value,
        year: document.getElementById('add-car-year').value,
        brand: document.getElementById('add-car-brand').value,
        color: document.getElementById('add-car-color').value,
        plate: document.getElementById('add-car-plate').value,
        seats: document.getElementById('add-car-seats').value,
        price: document.getElementById('add-car-price').value,
        type: document.getElementById('add-car-type').value,
        country: document.getElementById('add-car-country').value,
        status: document.getElementById('add-car-status').value,
        expenses: []
    };

    if (!carData.name || !carData.plate) {
        alert('Vui lòng nhập đầy đủ thông tin bắt buộc!');
        return;
    }

    const newId = 'C' + String(Date.now()).slice(-4);
    
    // In a real app, we'd send this to a server. 
    // Here we update the local carsList in common.js 
    if (typeof carsList !== 'undefined') {
        carsList.unshift({ id: newId, ...carData });
        alert('Thêm xe mới thành công!');
        window.location.href = 'QuanLyXe.html';
    }
}
