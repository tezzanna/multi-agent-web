document.addEventListener('DOMContentLoaded', function() {
    // Demo data
    const products = {1: 'Laptop', 2: 'Smartphone', 3: 'Tablet', 4: 'Headphones'};
    const customers = {1: 'Alice', 2: 'Bob', 3: 'Charlie', 4: 'Diana'};
    const regions = {1: 'North', 2: 'South', 3: 'East', 4: 'West'};
    const dates = {1: '2023-01-15', 2: '2023-02-20', 3: '2023-03-10', 4: '2023-04-05'};
    const sales = [
        {id:1, product_id:1, customer_id:1, region_id:1, date_id:1, quantity:2, unit_price:1200, total_price:2400, created_at:'2023-01-15'},
        {id:2, product_id:2, customer_id:2, region_id:2, date_id:2, quantity:5, unit_price:800, total_price:4000, created_at:'2023-02-20'},
        {id:3, product_id:3, customer_id:3, region_id:3, date_id:3, quantity:3, unit_price:600, total_price:1800, created_at:'2023-03-10'},
        {id:4, product_id:4, customer_id:4, region_id:4, date_id:4, quantity:10, unit_price:150, total_price:1500, created_at:'2023-04-05'},
        {id:5, product_id:1, customer_id:2, region_id:1, date_id:1, quantity:1, unit_price:1200, total_price:1200, created_at:'2023-01-15'},
        {id:6, product_id:2, customer_id:3, region_id:2, date_id:2, quantity:2, unit_price:800, total_price:1600, created_at:'2023-02-20'},
        {id:7, product_id:3, customer_id:4, region_id:3, date_id:3, quantity:4, unit_price:600, total_price:2400, created_at:'2023-03-10'},
        {id:8, product_id:4, customer_id:1, region_id:4, date_id:4, quantity:7, unit_price:150, total_price:1050, created_at:'2023-04-05'}
    ];
    // Create table
    const tableContainer = document.getElementById('tableContainer');
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['ID', 'Product', 'Customer', 'Region', 'Date', 'Qty', 'Unit Price', 'Total'].forEach(text => {const th=document.createElement('th'); th.textContent=text; headerRow.appendChild(th);});
    thead.appendChild(headerRow);
    table.appendChild(thead);
    const tbody = document.createElement('tbody');
    sales.forEach(rec=>{const tr=document.createElement('tr');
        const cells=[rec.id, products[rec.product_id], customers[rec.customer_id], regions[rec.region_id], dates[rec.date_id], rec.quantity, rec.unit_price, rec.total_price];
        cells.forEach(val=>{const td=document.createElement('td'); td.textContent=val; tr.appendChild(td);});
        tbody.appendChild(tr);});
    table.appendChild(tbody);
    tableContainer.appendChild(table);
    // Prepare chart data: total sales per product
    const totals = {};
    Object.keys(products).forEach(id=>{totals[id]=0;});
    sales.forEach(r=>{totals[r.product_id]+=r.total_price;});
    const ctx = document.getElementById('mainChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.values(products),
            datasets: [{
                label: 'Продажи',
                data: Object.values(totals),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});