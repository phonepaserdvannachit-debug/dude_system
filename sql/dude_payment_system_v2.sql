-- ===================================================
-- DUDE PAYMENT SHARING SYSTEM — Clean MariaDB schema v2
-- Generated from dude_payment_system.sql
-- Notes:
-- 1) Uses snake_case column names for FastAPI/SQLAlchemy.
-- 2) Stores BCrypt hashes, not plain text passwords.
-- 3) Adds production fields for bill details, slips, and timestamps.
-- ===================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `slip`;
DROP TABLE IF EXISTS `share`;
DROP TABLE IF EXISTS `bill_detail`;
DROP TABLE IF EXISTS `bill`;
DROP TABLE IF EXISTS `contract`;
DROP TABLE IF EXISTS `setting`;
DROP TABLE IF EXISTS `goods`;
DROP TABLE IF EXISTS `person`;
DROP TABLE IF EXISTS `type_of_bill`;
DROP TABLE IF EXISTS `category`;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `category` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `unit` VARCHAR(20) DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_category_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `type_of_bill` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type_name` VARCHAR(50) NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_type_of_bill_type_name` (`type_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `person` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `aka` VARCHAR(50) DEFAULT NULL,
  `profile_pic` VARCHAR(500) DEFAULT NULL,
  `user_name` VARCHAR(50) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `qr_code` VARCHAR(500) DEFAULT NULL,
  `is_admin` TINYINT(1) NOT NULL DEFAULT 0,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_person_user_name` (`user_name`),
  KEY `idx_person_is_admin` (`is_admin`),
  KEY `idx_person_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `goods` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `price` DECIMAL(12,2) DEFAULT NULL,
  `category_id` INT DEFAULT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_goods_category_id` (`category_id`),
  KEY `idx_goods_is_active` (`is_active`),
  CONSTRAINT `fk_goods_category` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `bill` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type_id` INT DEFAULT NULL,
  `total_value` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `paid_status` TINYINT(1) NOT NULL DEFAULT 0,
  `keeper_id` INT DEFAULT NULL,
  `bookkeeper_auto` TINYINT(1) NOT NULL DEFAULT 1,
  `bill_date` DATE NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_bill_type_id` (`type_id`),
  KEY `idx_bill_keeper_id` (`keeper_id`),
  KEY `idx_bill_paid_status` (`paid_status`),
  KEY `idx_bill_bill_date` (`bill_date`),
  CONSTRAINT `fk_bill_type` FOREIGN KEY (`type_id`) REFERENCES `type_of_bill` (`id`),
  CONSTRAINT `fk_bill_keeper` FOREIGN KEY (`keeper_id`) REFERENCES `person` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `bill_detail` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `bill_id` INT NOT NULL,
  `goods_id` INT DEFAULT NULL,
  `goods_name` VARCHAR(100) NOT NULL,
  `quantity` DECIMAL(10,2) NOT NULL DEFAULT 1.00,
  `unit_price` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `line_total` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `buyer_id` INT DEFAULT NULL,
  `buyer_other` VARCHAR(100) DEFAULT NULL,
  `reason` VARCHAR(255) DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_bill_detail_bill_id` (`bill_id`),
  KEY `idx_bill_detail_goods_id` (`goods_id`),
  KEY `idx_bill_detail_buyer_id` (`buyer_id`),
  CONSTRAINT `fk_bill_detail_bill` FOREIGN KEY (`bill_id`) REFERENCES `bill` (`id`),
  CONSTRAINT `fk_bill_detail_goods` FOREIGN KEY (`goods_id`) REFERENCES `goods` (`id`),
  CONSTRAINT `fk_bill_detail_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `person` (`id`),
  CONSTRAINT `chk_bill_detail_buyer_required` CHECK (`buyer_id` IS NOT NULL OR `buyer_other` IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `share` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `bill_id` INT NOT NULL,
  `payer_id` INT DEFAULT NULL,
  `payer_other` VARCHAR(100) DEFAULT NULL,
  `share_value` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `cost` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `net_value` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `paid_status` TINYINT(1) NOT NULL DEFAULT 0,
  `paid_at` DATETIME DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_share_bill_payer` (`bill_id`, `payer_id`),
  KEY `idx_share_bill_id` (`bill_id`),
  KEY `idx_share_payer_id` (`payer_id`),
  KEY `idx_share_paid_status` (`paid_status`),
  CONSTRAINT `fk_share_bill` FOREIGN KEY (`bill_id`) REFERENCES `bill` (`id`),
  CONSTRAINT `fk_share_payer` FOREIGN KEY (`payer_id`) REFERENCES `person` (`id`),
  CONSTRAINT `chk_share_payer_required` CHECK (`payer_id` IS NOT NULL OR `payer_other` IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `slip` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `share_id` INT NOT NULL,
  `storage_url` VARCHAR(500) NOT NULL,
  `file_name` VARCHAR(255) DEFAULT NULL,
  `file_type` VARCHAR(50) DEFAULT NULL,
  `file_size` INT DEFAULT NULL,
  `uploaded_by_id` INT DEFAULT NULL,
  `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_slip_share_id` (`share_id`),
  KEY `idx_slip_uploaded_by_id` (`uploaded_by_id`),
  CONSTRAINT `fk_slip_share` FOREIGN KEY (`share_id`) REFERENCES `share` (`id`),
  CONSTRAINT `fk_slip_uploaded_by` FOREIGN KEY (`uploaded_by_id`) REFERENCES `person` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `contract` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sender_id` INT NOT NULL,
  `message` TEXT NOT NULL,
  `is_read` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_contract_sender_id` (`sender_id`),
  KEY `idx_contract_created_at` (`created_at`),
  KEY `idx_contract_is_read` (`is_read`),
  CONSTRAINT `fk_contract_sender` FOREIGN KEY (`sender_id`) REFERENCES `person` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `setting` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `key_name` VARCHAR(50) NOT NULL,
  `value` VARCHAR(255) DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_setting_key_name` (`key_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `category` (`id`, `name`, `unit`, `created_at`, `updated_at`) VALUES
  (1, 'Beverage', 'bottle', '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (2, 'Pill', 'set', '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (3, 'Snack', 'piece', '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (4, 'Food', 'piece', '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (5, 'Material', 'piece', '2026-07-02 19:23:57', '2026-07-02 19:23:57');

INSERT INTO `type_of_bill` (`id`, `type_name`, `created_at`, `updated_at`) VALUES
  (1, 'DRINK', '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (2, 'FOOD', '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (3, 'OTHERS', '2026-07-02 19:23:57', '2026-07-02 19:23:57');

INSERT INTO `person` (`id`, `name`, `aka`, `profile_pic`, `user_name`, `password_hash`, `qr_code`, `is_admin`, `created_at`, `updated_at`) VALUES
  (1, 'Michael', 'Vice Head of Puusy', 'profiles/john_pic.jpeg', 'john', '$2y$12$/E7VZuDBXyPNXb7r30Lpr.fhIFYEEzDoWo8ZstGkgHGHEALa1mN4e', 'qr/john_qr.jpeg', 1, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (2, 'A TAR', 'Gen Z Manager', 'profiles/tar_pic.jpeg', 'tar', '$2y$12$2w4c6jVz9Rawt544MYRb/.M/20f4M9y7HoKjDFgiFn/zuFGk75e2a', 'qr/tar_qr.jpeg', 0, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (3, 'Lobster', 'Speech Manager', NULL, 'koung', '$2y$12$2w4c6jVz9Rawt544MYRb/.M/20f4M9y7HoKjDFgiFn/zuFGk75e2a', 'qr/koung_qr.jpeg', 0, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (4, 'SomLock', 'Pussy Teacher', NULL, 'sun', '$2y$12$2w4c6jVz9Rawt544MYRb/.M/20f4M9y7HoKjDFgiFn/zuFGk75e2a', NULL, 0, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (5, 'Aiy SomHee', 'Head of Pussy', 'profiles/top_pic.jpeg', 'top', '$2y$12$2w4c6jVz9Rawt544MYRb/.M/20f4M9y7HoKjDFgiFn/zuFGk75e2a', 'qr/top_qr.jpeg', 0, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (6, 'Daddy', 'Khayee Hee', 'profiles/dad_pic.jpeg', 'dan', '$2y$12$LgWc9sbeaiAUvRocfbgCOOXPXL3VGzAEUPZaXQcG6FqN1WdtBAd86', 'qr/dad_qr.jpeg', 0, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (7, 'NowImhurt', 'Siengda Founder', NULL, 'ko', '$2y$12$2w4c6jVz9Rawt544MYRb/.M/20f4M9y7HoKjDFgiFn/zuFGk75e2a', NULL, 0, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (8, 'VickAuan', 'Head Engineer', NULL, 'vick', '$2y$12$2w4c6jVz9Rawt544MYRb/.M/20f4M9y7HoKjDFgiFn/zuFGk75e2a', NULL, 0, '2026-07-02 19:23:57', '2026-07-02 19:23:57');

INSERT INTO `goods` (`id`, `name`, `price`, `category_id`, `created_at`, `updated_at`) VALUES
  (1, 'Oishi', 15000.0, 1, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (2, 'Yen Yen', 15000.0, 1, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (3, 'ChanKeow', 15000.0, 1, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (4, 'Namduem 5l', 25000.0, 1, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (5, 'Namduem 1.5l', 10000.0, 1, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (6, 'Kratom', 100000.0, 2, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (7, 'Nam ya', 75000.0, 2, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (8, 'Bai', 25000.0, 2, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (9, 'S5000', 5000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (10, 'S8000', 8000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (11, 'S10000', 10000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (12, 'S12000', 12000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (13, 'S15000', 15000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (14, 'S18000', 18000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (15, 'S20000', 20000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (16, 'S22000', 22000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (17, 'S25000', 25000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (18, 'S30000', 30000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (19, 'S35000', 35000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (20, 'S40000', 40000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (21, 'S45000', 45000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (22, 'S50000', 50000.0, 3, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (23, 'Sumlee', 20000.0, 5, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (24, 'Ice3', 3000.0, 5, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (25, 'Ice5', 5000.0, 5, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (26, 'Ice10', 10000.0, 5, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (27, 'Tizzu8', 8000.0, 5, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (28, 'Tizzu10', 10000.0, 5, '2026-07-02 19:23:57', '2026-07-02 19:23:57'),
  (29, 'Tizzu12', 12000.0, 5, '2026-07-02 19:23:57', '2026-07-02 19:23:57');

-- Passwords from the source dump were converted to BCrypt hashes.
-- Login test credentials are unchanged for now, for example john / 2580.
-- Change all real production passwords before deployment.
