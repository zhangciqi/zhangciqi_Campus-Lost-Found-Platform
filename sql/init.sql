-- 校园失物招领平台 V1.0 建库脚本
-- 使用 Navicat 或 mysql 客户端执行
CREATE DATABASE IF NOT EXISTS campus_lost_found DEFAULT CHARSET utf8mb4;
USE campus_lost_found;

CREATE TABLE users (
  user_id   INT PRIMARY KEY AUTO_INCREMENT,
  account   VARCHAR(50)  NOT NULL UNIQUE,
  password  VARCHAR(100) NOT NULL,
  name      VARCHAR(50)  NOT NULL,
  role      VARCHAR(20)  NOT NULL,
  phone     VARCHAR(20)
);

CREATE TABLE items (
  item_id       INT PRIMARY KEY AUTO_INCREMENT,
  info_type     VARCHAR(10)  NOT NULL,
  item_name     VARCHAR(100) NOT NULL,
  item_type     VARCHAR(30)  NOT NULL,
  location      VARCHAR(100) NOT NULL,
  event_time    DATETIME     NOT NULL,
  photos        VARCHAR(500),
  description   TEXT,
  review_status VARCHAR(20)  NOT NULL DEFAULT 'pending',
  item_status   VARCHAR(20)  NOT NULL DEFAULT 'unclaimed',
  publisher_id  INT NOT NULL,
  FOREIGN KEY (publisher_id) REFERENCES users(user_id),
  INDEX idx_type_status (info_type, review_status)
);

CREATE TABLE claims (
  claim_id      INT PRIMARY KEY AUTO_INCREMENT,
  item_id       INT NOT NULL,
  applicant_id  INT NOT NULL,
  claim_detail  TEXT NOT NULL,
  review_result VARCHAR(20) NOT NULL DEFAULT 'pending',
  handover_time DATETIME,
  FOREIGN KEY (item_id)      REFERENCES items(item_id),
  FOREIGN KEY (applicant_id) REFERENCES users(user_id)
);

-- 预置初始管理员：账号 admin，密码 admin123（bcrypt 加密存储）
INSERT INTO users(account, password, name, role)
VALUES('admin', '$2b$12$NrwcyJvR9jWepmZ5hu4gke3tqrTE6BwZIJXorqpP7y7uU8zmZT8zu', '系统管理员', 'admin');
