
ALTER TABLE `users` ADD CONSTRAINT `fk_users_roles` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`);

ALTER TABLE `folders` ADD CONSTRAINT `fk_folders_patients` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`);

ALTER TABLE `events` ADD CONSTRAINT `fk_events_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

ALTER TABLE `folder_visits` ADD CONSTRAINT `fk_folder_visits_folders` FOREIGN KEY (`folder_id`) REFERENCES `folders` (`folder_id`);

ALTER TABLE `payments` ADD CONSTRAINT `fk_folder_payments` FOREIGN KEY (`folder_id`) REFERENCES `folders` (`folder_id`);

ALTER TABLE `conversation` ADD CONSTRAINT `fk_conversation_user1` FOREIGN KEY (`user1_id`) REFERENCES `users` (`user_id`);

ALTER TABLE `conversation` ADD CONSTRAINT `fk_conversation_user2` FOREIGN KEY (`user2_id`) REFERENCES `users` (`user_id`);

ALTER TABLE `attachments` ADD CONSTRAINT `fk_attachments_folders` FOREIGN KEY (`folder_id`) REFERENCES `folders` (`folder_id`);

ALTER TABLE `appointments` ADD CONSTRAINT `fk_appointments_folders` FOREIGN KEY (`folder_id`) REFERENCES `folders` (`folder_id`);

ALTER TABLE `messages` ADD CONSTRAINT `fk_messages_conversation` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`conversation_id`);

ALTER TABLE `messages` ADD CONSTRAINT `fk_messages_sender` FOREIGN KEY (`sender_id`) REFERENCES `users` (`user_id`);

ALTER TABLE `notes` ADD CONSTRAINT `fk_notes_folders` FOREIGN KEY (`folder_id`) REFERENCES `folders` (`folder_id`);

ALTER TABLE `stocks` ADD CONSTRAINT `fk_stocks_medicine` FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`medicine_id`) ON DELETE CASCADE;

ALTER TABLE `stocks` ADD CONSTRAINT `fk_stocks_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`) ON DELETE SET NULL;

ALTER TABLE `stocks` ADD CONSTRAINT `fk_stocks_unit` FOREIGN KEY (`unit_id`) REFERENCES `units` (`unit_id`) ON DELETE CASCADE;

ALTER TABLE `logs_stock` ADD CONSTRAINT `fk_logs_stock` FOREIGN KEY (`stock_id`) REFERENCES `stocks` (`stock_id`) ON DELETE CASCADE;



CREATE TABLE `users` (
  `id` CHAR(36) PRIMARY KEY NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role_id` BIGINT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `name` VARCHAR(255) NOT NULL
);

CREATE TABLE `roles` (
  `id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `conversation` (
  `conversation_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `user1_id` BIGINT NOT NULL,
  `user2_id` BIGINT NOT NULL,
  `last_message` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `messages` (
  `message_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `conversation_id` BIGINT NOT NULL,
  `sender_id` BIGINT NOT NULL,
  `message` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `patients` (
  `id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT,
  `patient_name` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `notes` TEXT,
  `diseases` TEXT NOT NULL,
  `gender` ENUM ('Male', 'Female') NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `age` INT NOT NULL
);

CREATE TABLE `folders` (
  `id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `folder_name` VARCHAR(255) NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `status` ENUM ('Active', 'Completed', 'Archived') NOT NULL,
  `patient_id` BIGINT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `attachments` (
  `attachment_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `file_name` VARCHAR(255) NOT NULL,
  `file_url` VARCHAR(255) NOT NULL,
  `file_type` VARCHAR(50) NOT NULL,
  `file_size` BIGINT NOT NULL,
  `attachable_type` VARCHAR(50) NOT NULL,
  `attachable_id` VARCHAR(255) NOT NULL,
  `folder_id` BIGINT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `notes` (
  `note_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `content` TEXT NOT NULL,
  `folder_id` BIGINT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `appointments` (
  `id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `status` ENUM ('Pending', 'Confirmed', 'Cancelled') NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `folder_id` BIGINT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `payments` (
  `id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `amount` DECIMAL(10,2) NOT NULL,
  `folder_id` BIGINT,
  `type` ENUM ('income', 'refund') NOT NULL,
  `note` TEXT,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `folder_visits` (
  `id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `dentist_id` BIGINT NOT NULL,
  `reason_of_visit` TEXT NOT NULL,
  `treatment_details` TEXT NOT NULL,
  `folder_id` BIGINT NOT NULL
);

CREATE TABLE `events` (
  `id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `start` DATE NOT NULL,
  `end` DATE NOT NULL,
  `location` TEXT NOT NULL,
  `user_id` CHAR(36) NOT NULL,
  `people` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `medicines` (
  `medicine_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) UNIQUE NOT NULL,
  `description` TEXT
);

CREATE TABLE `units` (
  `unit_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE `suppliers` (
  `supplier_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) UNIQUE NOT NULL,
  `contact_info` TEXT
);

CREATE TABLE `stocks` (
  `stock_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `medicine_id` BIGINT NOT NULL,
  `supplier_id` BIGINT,
  `unit_id` BIGINT NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `quantity` INT NOT NULL,
  `expiry_date` DATE NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE `logs_stock` (
  `log_stock_id` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `stock_id` BIGINT NOT NULL,
  `action` ENUM ('purchase', 'usage') NOT NULL,
  `quantity` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  `updated_at` TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);
