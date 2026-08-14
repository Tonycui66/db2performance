-- Database initialization script for performance benchmark
-- This script creates the necessary tables and test data

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    amount DECIMAL(10,2) NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Insert sample data for testing
INSERT INTO users (name, email) VALUES 
('Alice Johnson', 'alice@example.com'),
('Bob Smith', 'bob@example.com'),
('Charlie Brown', 'charlie@example.com'),
('Diana Prince', 'diana@example.com'),
('Eve Adams', 'eve@example.com');

INSERT INTO products (name, price, category) VALUES 
('Laptop', 999.99, 'Electronics'),
('Phone', 699.99, 'Electronics'),
('Tablet', 299.99, 'Electronics'),
('Headphones', 199.99, 'Electronics'),
('Keyboard', 79.99, 'Electronics'),
('Monitor', 299.99, 'Electronics'),
('Mouse', 29.99, 'Electronics'),
('Desk', 199.99, 'Furniture'),
('Chair', 299.99, 'Furniture'),
('Lamp', 49.99, 'Furniture');

INSERT INTO orders (user_id, product_id, amount, status) VALUES 
(1, 1, 999.99, 'completed'),
(1, 2, 699.99, 'shipped'),
(2, 3, 299.99, 'completed'),
(3, 4, 199.99, 'pending'),
(4, 5, 79.99, 'completed'),
(5, 6, 299.99, 'shipped'),
(1, 7, 199.99, 'completed'),
(2, 8, 199.99, 'pending'),
(3, 9, 299.99, 'completed'),
(4, 10, 49.99, 'shipped');

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES 
(1, 1, 1, 999.99),
(2, 2, 1, 699.99),
(3, 3, 1, 299.99),
(4, 4, 1, 199.99),
(5, 5, 1, 79.99),
(6, 6, 1, 299.99),
(7, 7, 1, 199.99),
(8, 8, 1, 199.99),
(9, 9, 1, 299.99),
(10, 10, 1, 49.99);

-- Create view for order summary
CREATE OR REPLACE VIEW order_summary AS
SELECT 
    o.id,
    o.user_id,
    u.name as user_name,
    o.product_id,
    p.name as product_name,
    o.amount,
    o.status,
    o.created_at,
    o.updated_at
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
