CREATE DATABASE IF NOT EXISTS community_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE community_portal;
CREATE TABLE members (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 full_name VARCHAR(150) NOT NULL,
 email VARCHAR(254) NOT NULL UNIQUE,
 phone VARCHAR(30), city VARCHAR(100), skills TEXT,
 experience_years DECIMAL(4,1), password_hash VARCHAR(255) NOT NULL,
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE uploaded_files (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 member_id BIGINT NOT NULL,
 original_filename VARCHAR(255) NOT NULL,
 s3_key VARCHAR(1024) NOT NULL UNIQUE,
 content_type VARCHAR(150), file_size BIGINT NOT NULL,
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_uploaded_files_member_id (member_id),
 CONSTRAINT fk_uploaded_files_member FOREIGN KEY (member_id) REFERENCES members(id)
);
