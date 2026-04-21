document.addEventListener('DOMContentLoaded', () => {
    // Demo data
    const categories = [
        { id: 1, name: 'Electronics', description: 'Electronic devices' },
        { id: 2, name: 'Books', description: 'Printed books' },
        { id: 3, name: 'Clothing', description: 'Apparel' }
    ];
    const products = [
        { id: 1, name: 'Smartphone', description: 'Android phone', price: 599.99, stockQuantity: 120, categoryId: 1 },
        { id: 2, name: 'Laptop', description: 'Gaming laptop', price: 1299.99, stockQuantity: 80, categoryId: 1 },
        { id: 3, name: 'Headphones', description: 'Noise cancelling', price: 199.99, stockQuantity: 200, categoryId: 1 },
        { id: 4, name: 'Novel', description: 'Fiction book', price: 14.99, stockQuantity: 300, categoryId: 2 },
        { id: 5, name: 'Biography', description: 'Life story', price: 19.99, stockQuantity: 250, categoryId: 2 },
        { id: 6, name: 'T-Shirt', description: 'Cotton tee', price: 24.99, stockQuantity: 400, categoryId: 3 },
        { id: 7, name: 'Jeans', description: 'Denim jeans', price: 49.99, stockQuantity: 350, categoryId: 3 },
        { id: 8, name: 'Jacket', description: 'Winter jacket', price: 89.99, stockQuantity: 150, categoryId: 3 }
    ];
    const customers = [
        { id: 1, firstName: 'Alice', lastName: 'Smith', email: 'alice@example.com', phone: '555-0101', createdAt: '2022-01-15' },
        { id: 2, firstName: 'Bob', lastName: 'Johnson', email: 'bob@example.com', phone: '555-0102', createdAt: '2022-02-20' },
        { id: 3, firstName: 'Carol', lastName: 'Williams', email: 'carol@example.com', phone: '555-0103', createdAt: '2022-03-05' },
        { id: 4, firstName: 'David', lastName: 'Brown', email: 'david@example.com', phone: '555-0104', createdAt: '2022-04-12' },
        { id: 5, firstName: 'Eve', lastName: 'Jones', email: 'eve@example.com', phone: '555-0105', createdAt: '2022-05-18' },
        { id: 6, firstName: 'Frank', lastName: 'Garcia', email: 'frank@example.com', phone: '555-0106', createdAt: '2022-06-22' },
        { id: 7, firstName: 'Grace', lastName: 'Miller', email: 'grace@example.com', phone: '555-0107', createdAt: '2022-07-30' },
        { id: 8, firstName: 'Hank', lastName: 'Davis', email: 'hank@example.com', phone: '555-0108', createdAt: '2022-08-14' }
    ];
    const orders = [
        { id: 1, customerId: 1, orderDate: '2023-08-01', status: 'PAID', totalAmount: 719.98 },
        { id: 2, customerId: 2, orderDate: '2023-08-02', status: 'PAID', totalAmount: 1499.98 },
        { id: 3, customerId: 3, orderDate: '2023-08-03', status: 'NEW', totalAmount: 199.99 },
        { id: 4, customerId: 4, orderDate: '2023-08-04', status: 'PAID', totalAmount: 24.99 },
        { id: 5, customerId: 5, orderDate: '2023-08-05', status: 'PAID', totalAmount: 49.99 },
        { id: 6, customerId: 6, orderDate: '2023-08-06', status: 'PAID', totalAmount: 89.99 },
        { id: 7, customerId: 7, orderDate: '2023-08-07', status: 'PAID', totalAmount: 1199.98 },
        { id: 8, customerId: 8, orderDate: '2023-08-08', status: 'PAID', totalAmount: 199.99 }
    ];
    const orderItems = [
        { id: 1, orderId: 1, productId: 1, quantity: 1, unitPrice: 599.99, totalPrice: 599.99 },
        { id: 2, orderId: 1, productId: 3, quantity: 1, unitPrice: 199.99, totalPrice: 199.99 },
        { id: 3, orderId: 2, productId: 2, quantity: 1, unitPrice: 1299.99, totalPrice: 1299.99 },
        { id: 4, orderId: 2, productId: 3, quantity: 1, unitPrice: 199.99, totalPrice: 199.99 },
        { id: 5, orderId: 3, productId: 3, quantity: 1, unitPrice: 199.99, totalPrice: 199.99 },
        { id: 6, orderId: 4, productId: 6, quantity: 1, unitPrice: 24.99, totalPrice: 24.99 },
        { id: 7, orderId: 5, productId: 7, quantity: 1, unitPrice: 49.99, totalPrice: 49.99 },
        { id: 8, orderId: 6, productId: 8, quantity: 1, unitPrice: 89.99, totalPrice: 89.99 },
        { id: 9, orderId: 7, productId: 1, quantity: 1, unitPrice: 599.99, totalPrice: 599.99 },
        { id:10, orderId: 7, productId: 2, quantity: 1, unitPrice: 599.99, totalPrice: 599.99 },
        { id:11, orderId: 8, productId: 3, quantity: 1, unitPrice: 199.99, totalPrice: 199.99 }
    ];
    const salesRecords = [];
    const startDate = new Date('2023-07-25');
    for (let i = 0; i < 14; i++) {
        const current = new Date(startDate);
        current.setDate(current.getDate() + i);
        const dateStr = current.toISOString().split('T')[0];
        products.forEach(p => {
            const units = Math.floor(Math.random() * 10);
            const revenue = units * p.price;
            salesRecords.push({ date: dateStr, productId: p.id, unitsSold: units, revenue: revenue });
        });
    }
    const users = [
        { id: 1, username: 'admin', passwordHash: 'hash', role: 'ADMIN' },
        { id: 2, username: 'analyst', passwordHash: 'hash', role: 'ANALYST' }
    ];

    // DOM elements
    const container = document.getElementById('dashboard') || document.body;
    const filterDiv = document.createElement('div');
    filterDiv.style.marginBottom = '20px';

    // Date filters
    const startLabel = document.createElement('label');
    startLabel.textContent = 'Start Date: ';
    const startInput = document.createElement('input');
    startInput.type = 'date';
    startLabel.appendChild(startInput);
    filterDiv.appendChild(startLabel);

    const endLabel = document.createElement('label');
    endLabel.textContent = ' End Date: ';
    const endInput = document.createElement('input');
    endInput.type = 'date';
    endLabel.appendChild(endInput);
    filterDiv.appendChild(endLabel);

    // Product filter
    const productLabel = document.createElement('label');
    productLabel.textContent = ' Product: ';
    const productSelect = document.createElement('select');
    const allOption = document.createElement('option');
    allOption.value = '';
    allOption.textContent = 'All';
    productSelect.appendChild(allOption);
    products.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.name;
        productSelect.appendChild(opt);
    });
    productLabel.appendChild(productSelect);
    filterDiv.appendChild(productLabel);

    // Search input
    const searchLabel = document.createElement('label');
    searchLabel.textContent = ' Search: ';
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchLabel.appendChild(searchInput);
    filterDiv.appendChild(searchLabel);

    container.appendChild(filterDiv);

    // Table
    const table = document.createElement('table');
    table.border = '1';
    table.style.borderCollapse = 'collapse';
    table.style.width = '100%';
    container.appendChild(table);

    // Chart
    const canvas = document.getElementById('mainChart');
    if (!canvas) {
        const newCanvas = document.createElement('canvas');
        newCanvas.id = 'mainChart';
        newCanvas.width = 800;
        newCanvas.height = 400;
        container.appendChild(newCanvas);
    }
    const ctx = document.getElementById('mainChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Revenue',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Date' } },
                y: { title: { display: true, text: 'Revenue ($)' }, beginAtZero: true }
            }
        }
    });

    // State
    let filteredRecords = [...salesRecords];
    let sortColumn = 'date';
    let sortAsc = true;

    // Helper functions
    function getProductName(id) {
        const p = products.find(pr => pr.id === id);
        return p ? p.name : 'Unknown';
    }
    function applyFilters() {
        const startVal = startInput.value;
        const endVal = endInput.value;
        const productVal = productSelect.value;
        const searchVal = searchInput.value.toLowerCase();

        filteredRecords = salesRecords.filter(rec => {
            let ok = true;
            if (startVal) ok = ok && (rec.date >= startVal);
            if (endVal) ok = ok && (rec.date <= endVal);
            if (productVal) ok = ok && (rec.productId == productVal);
            if (searchVal) {
                const pname = getProductName(rec.productId).toLowerCase();
                ok = ok && pname.includes(searchVal);
            }
            return ok;
        });
        sortRecords();
        renderTable();
        renderChart();
    }
    function sortRecords() {
        filteredRecords.sort((a, b) => {
            let valA, valB;
            if (sortColumn === 'date') {
                valA = a.date;
                valB = b.date;
            } else if (sortColumn === 'product') {
                valA = getProductName(a.productId);
                valB = getProductName(b.productId);
            } else if (sortColumn === 'units') {
                valA = a.unitsSold;
                valB = b.unitsSold;
            } else if (sortColumn === 'revenue') {
                valA = a.revenue;
                valB = b.revenue;
            }
            if (valA < valB) return sortAsc ? -1 : 1;
            if (valA > valB) return sortAsc ? 1 : -1;
            return 0;
        });
    }
    function renderTable() {
        table.innerHTML = '';
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        const headers = [
            { key: 'date', text: 'Date' },
            { key: 'product', text: 'Product' },
            { key: 'units', text: 'Units Sold' },
            { key: 'revenue', text: 'Revenue ($)' }
        ];
        headers.forEach(h => {
            const th = document.createElement('th');
            th.textContent = h.text;
            th.style.cursor = 'pointer';
            th.addEventListener('click', () => {
                if (sortColumn === h.key) sortAsc = !sortAsc;
                else { sortColumn = h.key; sortAsc = true; }
                applyFilters();
            });
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        filteredRecords.forEach(rec => {
            const tr = document.createElement('tr');
            const tdDate = document.createElement('td');
            tdDate.textContent = rec.date;
            tr.appendChild(tdDate);
            const tdProd = document.createElement('td');
            tdProd.textContent = getProductName(rec.productId);
            tr.appendChild(tdProd);
            const tdUnits = document.createElement('td');
            tdUnits.textContent = rec.unitsSold;
            tr.appendChild(tdUnits);
            const tdRev = document.createElement('td');
            tdRev.textContent = rec.revenue.toFixed(2);
            tr.appendChild(tdRev);
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
    }
    function renderChart() {
        const labelsMap = {};
        filteredRecords.forEach(rec => {
            if (!labelsMap[rec.date]) labelsMap[rec.date] = 0;
            labelsMap[rec.date] += rec.revenue;
        });
        const labels = Object.keys(labelsMap).sort();
        const data = labels.map(d => labelsMap[d].toFixed(2));
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update();
    }

    // Event listeners
    startInput.addEventListener('change', applyFilters);
    endInput.addEventListener('change', applyFilters);
    productSelect.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', applyFilters);

    // Initial render
    applyFilters();
});