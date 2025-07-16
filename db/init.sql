-- 创建用户表
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT false,
    hashed_password VARCHAR(255) NOT NULL
);

-- 创建规则表
CREATE TABLE IF NOT EXISTS rule (
    id SERIAL PRIMARY KEY,
    pattern TEXT NOT NULL,
    description TEXT,
    data_type VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    reference_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建规则提交表
CREATE TABLE IF NOT EXISTS rule_submission (
    id SERIAL PRIMARY KEY,
    pattern TEXT NOT NULL,
    description TEXT NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    reference_path TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    submitted_by_id INTEGER REFERENCES "user"(id),
    reviewed_by_id INTEGER REFERENCES "user"(id),
    rule_id INTEGER REFERENCES rule(id),
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    review_notes TEXT
);

-- 创建管理员用户
INSERT INTO "user" (email, full_name, is_admin, hashed_password)
VALUES ('admin@bioregex.com', 'Admin User', true, '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW')
ON CONFLICT (email) DO NOTHING;

-- 初始规则数据示例
INSERT INTO rule (pattern, description, data_type, region)
VALUES 
    ('^[A-Z]{3}\d{5}$', 'FDA Standard Patient ID', 'Patient ID', 'FDA'),
    ('^\d{4}-\d{2}-\d{2}$', 'ISO Date Format', 'Date', 'Global'),
    ('^EU-\d{3}-\d{4}-\d{4}$', 'EMA Patient ID Format', 'Patient ID', 'EMA')
ON CONFLICT (pattern) DO NOTHING;
