CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64) UNIQUE NOT NULL,
    machine_code VARCHAR(64),
    email VARCHAR(128),
    password_hash VARCHAR(256),
    is_active BOOLEAN DEFAULT TRUE,
    is_vip BOOLEAN DEFAULT TRUE,
    expired_at TIMESTAMP DEFAULT '2099-12-31 23:59:59',
    left_count INTEGER DEFAULT 999999,
    registered BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    chn_name VARCHAR(128),
    icon VARCHAR(256),
    sort_order INTEGER DEFAULT 0,
    status CHAR(1) DEFAULT 'A'
);

CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(128) NOT NULL,
    icon VARCHAR(256),
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS series (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    name VARCHAR(128) NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS phone_models (
    id SERIAL PRIMARY KEY,
    series_id INTEGER REFERENCES series(id),
    brand_id INTEGER REFERENCES brands(id),
    model_name VARCHAR(256) NOT NULL,
    plt_file VARCHAR(256),
    plt_url VARCHAR(512),
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS plt_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(256) NOT NULL,
    original_url VARCHAR(512),
    encrypted_data BYTEA,
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS print_jobs (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64),
    model_name VARCHAR(256),
    image_data TEXT,
    status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
