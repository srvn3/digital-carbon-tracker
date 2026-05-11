CREATE DATABASE IF NOT EXISTS digital_carbon_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE digital_carbon_tracker;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    green_score INT DEFAULT 75,
    joined_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS apps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_key VARCHAR(50) NOT NULL UNIQUE,
    app_name VARCHAR(100) NOT NULL,
    unit_label VARCHAR(50) NOT NULL,
    emission_factor DECIMAL(6,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS app_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    usage_date DATE NOT NULL,
    total_co2 DECIMAL(10,2) DEFAULT 0,
    notes VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_usage_date (user_id, usage_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS app_usage_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_usage_id INT NOT NULL,
    app_id INT NOT NULL,
    usage_amount DECIMAL(8,2) NOT NULL,
    co2_value DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_usage_id) REFERENCES app_usage(id) ON DELETE CASCADE,
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS carbon_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    report_date DATE NOT NULL,
    total_co2 DECIMAL(10,2) NOT NULL,
    daily_co2 DECIMAL(10,2) NOT NULL,
    weekly_co2 DECIMAL(10,2) NOT NULL,
    monthly_co2 DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    level ENUM('info','warning','success') NOT NULL DEFAULT 'info',
    created_at DATETIME NOT NULL,
    read_status TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT IGNORE INTO apps (app_key, app_name, unit_label, emission_factor) VALUES
    ('instagram', 'Instagram', 'hours', 80.00),
    ('whatsapp', 'WhatsApp', 'hours', 3.00),
    ('youtube', 'YouTube', 'hours', 95.00),
    ('netflix', 'Netflix', 'hours', 120.00),
    ('gmail', 'Gmail', 'emails', 4.00),
    ('drive', 'Google Drive', 'GB', 2.00),
    ('spotify', 'Spotify', 'hours', 55.00),
    ('zoom', 'Zoom', 'hours', 90.00);

CREATE INDEX idx_app_usage_user_date ON app_usage(user_id, usage_date);
CREATE INDEX idx_usage_detail_app ON app_usage_detail(app_id);
CREATE INDEX idx_usage_detail_session ON app_usage_detail(app_usage_id);
CREATE INDEX idx_reports_user_date ON carbon_reports(user_id, report_date);
CREATE INDEX idx_notifications_user ON notifications(user_id);
