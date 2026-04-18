/* ============================================
   COMMON JAVASCRIPT - CAR FOR RENT SYSTEM
   Dùng chung cho tất cả các module
   ============================================ */

// --- FLATPICKR INITIALIZATION ---
const fpConfig = {
    wrap: true,
    locale: "vn",
    dateFormat: "d/m/Y",
    allowInput: true,
    monthSelectorType: "static",
    position: "auto right"
};

const fpDateTimeConfig = {
    ...fpConfig,
    enableTime: true,
    dateFormat: "d/m/Y H:i",
    time_24hr: true,
};

document.addEventListener('DOMContentLoaded', function () {
    // Target the wrapping containers instead of just the inputs
    document.querySelectorAll('.fp-wrap').forEach(wrap => {
        const input = wrap.querySelector('input');
        if (!input) return;

        // Priority for data-time attribute, fallback to ID check
        const isStart = input.id.includes('contract-start');
        const isEnd = input.id.includes('contract-end');
        const enableTime = wrap.dataset.time === 'true' || isStart || isEnd;
        
        let config = enableTime ? { ...fpDateTimeConfig } : { ...fpConfig };
        
        // Block past dates for Start and End dates
        if (isStart || isEnd) {
            config.minDate = "today";
        }

        if (typeof flatpickr !== 'undefined') {
            const fp = flatpickr(wrap, config);

            // If this is the start date, we want to update the end date's minDate when changed
            if (isStart) {
                fp.config.onChange.push(function(selectedDates, dateStr) {
                    const endWrap = document.querySelector('[id$="contract-end"]')?.closest('.fp-wrap');
                    if (endWrap && endWrap._flatpickr) {
                        endWrap._flatpickr.set('minDate', dateStr || "today");
                    }
                });
            }
        }
    });
});

// --- GLOBAL DATA ---
let customersList = [
    { id: 'KH001', name: 'Nguyễn Văn An', phone: '0909123456', cccd: '079090000111', rentCount: 2 },
    { id: 'KH002', name: 'Trần Thị Bích', phone: '0912888999', cccd: '079090000222', rentCount: 1 },
    { id: 'KH003', name: 'Lê Văn Cường', phone: '0988777666', cccd: '079090000333', rentCount: 0 }
];

let countriesList = [
    { id: 1, name: 'Nhật Bản' },
    { id: 2, name: 'Hàn Quốc' },
    { id: 3, name: 'Việt Nam' },
    { id: 4, name: 'Mỹ' },
    { id: 5, name: 'Đức' }
];

let carBrandsList = [
    { id: 1, name: 'Toyota', countryId: 1 },
    { id: 2, name: 'Honda', countryId: 1 },
    { id: 3, name: 'Mazda', countryId: 1 },
    { id: 4, name: 'Hyundai', countryId: 2 },
    { id: 5, name: 'Ford', countryId: 4 },
    { id: 6, name: 'Kia', countryId: 2 }
];

let carStylesList = [
    { id: 1, name: 'Sedan' },
    { id: 2, name: 'SUV' },
    { id: 3, name: 'MPV' },
    { id: 4, name: 'Hatchback' },
    { id: 5, name: 'Bán tải' }
];

let carModelsList = [
    { id: 1, name: 'Camry', brandId: 1, styleId: 1, seats: 5, description: 'Dòng sedan hạng D cao cấp' },
    { id: 2, name: 'Vios', brandId: 1, styleId: 1, seats: 5, description: 'Xe gia đình phổ biến' },
    { id: 3, name: 'CR-V', brandId: 2, styleId: 2, seats: 7, description: 'SUV Nhật Bản mạnh mẽ' },
    { id: 4, name: 'Mazda 3', brandId: 3, styleId: 1, seats: 5, description: 'Thiết kế KODO trẻ trung' },
    { id: 5, name: 'Innova', brandId: 1, styleId: 3, seats: 7, description: 'Xe MPV chuyên chở khách' },
    { id: 6, name: 'SantaFe', brandId: 4, styleId: 2, seats: 7, description: 'SUV Hàn Quốc hiện đại' },
    { id: 7, name: 'Fortuner', brandId: 1, styleId: 2, seats: 7, description: 'SUV địa hình bền bỉ' }
];

let carColorsList = [
    { id: 1, name: 'Trắng' },
    { id: 2, name: 'Đen' },
    { id: 3, name: 'Đỏ' },
    { id: 4, name: 'Xanh Dương' },
    { id: 5, name: 'Xám' },
    { id: 6, name: 'Bạc' }
];

let carsList = [
    { id: 'C001', name: 'Camry', year: '2023', brand: 'Toyota', plate: '51H-123.45', seats: 5, price: '800.000', priceHour: '100.000', status: 'Còn xe', type: 'Sedan', color: 'Trắng', country: 'Nhật Bản', expenses: [] },
    { id: 'C002', name: 'CR-V', year: '2024', brand: 'Honda', plate: '51K-678.90', seats: 7, price: '1.200.000', priceHour: '150.000', status: 'Còn xe', type: 'SUV', color: 'Đen', country: 'Nhật Bản', expenses: [] },
    { id: 'C003', name: 'Mazda 3', year: '2023', brand: 'Mazda', plate: '51G-555.22', seats: 4, price: '1.500.000', priceHour: '200.000', status: 'Đã thuê', type: 'Sedan', color: 'Đỏ', country: 'Nhật Bản', expenses: [] },
    { id: 'C004', name: 'Vios', year: '2022', brand: 'Toyota', plate: '53H-678.36', seats: 5, price: '700.000', priceHour: '80.000', status: 'Còn xe', type: 'Sedan', color: 'Bạc', country: 'Việt Nam', expenses: [] },
    { id: 'C005', name: 'Fortuner', year: '2021', brand: 'Toyota', plate: '51A-987.65', seats: 7, price: '1.300.000', priceHour: '180.000', status: 'Bảo trì', type: 'SUV', color: 'Xám', country: 'Nhật Bản', expenses: [] }
];

// --- CONTRACT DATA ---
let contractListDb = [
    { id: 'HD-8821', customer: 'Hoàng Thị A', carName: 'Mazda 3', carPlate: '30A-123.45', dueDate: '10:00 17/01', status: 'overdue', statusHtml: '<span class="badge-red">Quá hạn 1 ngày</span>', total: '1.600.000' },
    { id: 'HD-8825', customer: 'Lê Thị C', carName: 'Honda City', carPlate: '29C-999.88', dueDate: '08:00 18/01', status: 'overdue', statusHtml: '<span class="badge-red">Vừa quá hạn</span>', total: '1.000.000' },
    { id: 'HD-9001', customer: 'Hồ Văn V', carName: 'Kia Cerato', carPlate: '51F-555.66', dueDate: '16:00 Hôm nay', status: 'active', statusHtml: '<span class="badge-yellow">Sắp đến hạn</span>', total: '1.500.000' },
    { id: 'HD-9005', customer: 'Công Ty MNP', carName: 'Innova 2022', carPlate: '60A-111.11', dueDate: '17:30 Hôm nay', status: 'active', statusHtml: '<span class="badge-yellow">Sắp đến hạn</span>', total: '1.800.000' },
    { id: 'HD-9015', customer: 'Nguyễn Viết D', carName: 'Huyndai', carPlate: '51H-511.69', dueDate: '15:00 15/01', status: 'returned', statusHtml: '<span class="badge-green">Đã trả</span>', total: '1.500.000' }
];

// --- STATS DATA ---
const statsData = {
    'hom-nay': {
        label: 'Hôm nay',
        doanhThu: '7.000.000đ',
        soHopDong: '5',
        canXuLy: '4',
        topXe: [
            { name: 'Mazda 3', hoDong: '2 HĐ', rank: 1, percent: '50%' },
            { name: 'Vios 2023', hoDong: '1 HĐ', rank: 2, percent: '25%' },
            { name: 'Honda City', hoDong: '1 HĐ', rank: 3, percent: '25%' }
        ]
    },
    'hom-qua': {
        label: 'Hôm qua',
        doanhThu: '14.000.000đ',
        soHopDong: '10',
        canXuLy: '4',
        topXe: [
            { name: 'Mazda 3', hoDong: '6 HĐ', rank: 1, percent: '60%' },
            { name: 'Vios 2023', hoDong: '2 HĐ', rank: 2, percent: '20%' },
            { name: 'Honda City', hoDong: '2 HĐ', rank: 3, percent: '20%' }
        ]
    },
    '7-ngay': {
        label: '7 ngày',
        doanhThu: '36.000.000đ',
        soHopDong: '43',
        canXuLy: '4',
        topXe: [
            { name: 'Mazda 3', hoDong: '18 HĐ', rank: 1, percent: '50%' },
            { name: 'Vios 2023', hoDong: '9 HĐ', rank: 2, percent: '25%' },
            { name: 'Honda City', hoDong: '9 HĐ', rank: 3, percent: '25%' }
        ]
    },
    'thang-nay': {
        label: 'Tháng này',
        doanhThu: '74.000.000đ',
        soHopDong: '99',
        canXuLy: '4',
        topXe: [
            { name: 'Mazda 3', hoDong: '56 HĐ', rank: 1, percent: '50%' },
            { name: 'Vios 2023', hoDong: '28 HĐ', rank: 2, percent: '25%' },
            { name: 'Honda City', hoDong: '28 HĐ', rank: 3, percent: '25%' }
        ]
    }
};

// --- NAVIGATION ---
function switchView(viewId, element) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    if (element) {
        element.classList.add('active');
    }

    // Hide all views
    document.querySelectorAll('.view-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target view
    const targetView = document.getElementById('view-' + viewId);
    if (targetView) {
        targetView.classList.add('active');
    }

    window.scrollTo(0, 0);
}

// --- MODAL UTILITIES ---
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// --- SEARCH DROPDOWN UTILITIES ---
function showDropdown(id) {
    const dropdown = document.getElementById(id);
    if (dropdown) {
        dropdown.classList.add('active');
    }
}

function hideDropdown(id) {
    setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
    }, 200);
}

// Close dropdowns when clicking outside
document.addEventListener('click', function (e) {
    if (!e.target.closest('.search-container')) {
        document.querySelectorAll('.search-dropdown').forEach(d => d.classList.remove('active'));
    }
});

// --- DELETION CONFIRMATION ---
function openConfirmDelete(action, message = 'Bạn có chắc chắn muốn xóa?') {
    if (confirm(message)) {
        if (typeof action === 'function') {
            action();
        }
    }
}

// --- FORMATTING UTILITIES ---
function formatCurrency(value) {
    if (!value) return "0";
    return new Intl.NumberFormat('vi-VN').format(value);
}

function parseCurrency(value) {
    return parseInt(value.replace(/[^0-9]/g, '')) || 0;
}

function removeAccents(str) {
    if (!str) return '';
    return str.toString().normalize('NFD')
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/đ/g, "d")
        .replace(/Đ/g, "d")
        .toLowerCase()
        .trim();
}

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', function() {
    // Any global initialization
    console.log('Common JS loaded');
});
