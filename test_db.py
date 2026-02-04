import sqlite3
import random
from datetime import datetime, timedelta
print("begin")
# Create database
conn = sqlite3.connect('data/sample_sales.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    city TEXT,
    country TEXT,
    signup_date DATE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    price REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    order_date DATE,
    total_amount REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
''')

# Insert sample data
customers = [
    ('John Doe', 'john@email.com', 'New York', 'USA'),
    ('Jane Smith', 'jane@email.com', 'London', 'UK'),
    ('Bob Johnson', 'bob@email.com', 'Toronto', 'Canada'),
    ('Alice Brown', 'alice@email.com', 'Sydney', 'Australia'),
    ('Charlie Wilson', 'charlie@email.com', 'Paris', 'France'),
]

for i, (name, email, city, country) in enumerate(customers, 1):
    signup_date = datetime.now() - timedelta(days=random.randint(30, 365))
    cursor.execute(
        'INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)',
        (i, name, email, city, country, signup_date.strftime('%Y-%m-%d'))
    )

products = [
    ('Laptop', 'Electronics', 999.99),
    ('Mouse', 'Electronics', 29.99),
    ('Keyboard', 'Electronics', 79.99),
    ('Monitor', 'Electronics', 299.99),
    ('Desk Chair', 'Furniture', 199.99),
    ('Desk', 'Furniture', 399.99),
    ('Notebook', 'Stationery', 4.99),
    ('Pen Set', 'Stationery', 12.99),
]

for i, (name, category, price) in enumerate(products, 1):
    cursor.execute(
        'INSERT INTO products VALUES (?, ?, ?, ?)',
        (i, name, category, price)
    )

# Insert orders
for i in range(1, 51):
    customer_id = random.randint(1, 5)
    product_id = random.randint(1, 8)
    quantity = random.randint(1, 5)
    order_date = datetime.now() - timedelta(days=random.randint(1, 90))
    
    cursor.execute('SELECT price FROM products WHERE product_id = ?', (product_id,))
    price = cursor.fetchone()[0]
    total = price * quantity
    
    cursor.execute(
        'INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)',
        (i, customer_id, product_id, quantity, order_date.strftime('%Y-%m-%d'), total)
    )

conn.commit()
conn.close()
print("✅ Sample database created successfully!")