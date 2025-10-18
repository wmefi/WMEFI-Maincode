-- MySQL schema for wtestapp models (MySQL 5.7+/MySQL 8.0+/MariaDB 10.2+)
-- Engine: InnoDB, Charset: utf8mb4
-- Matches wtestapp/models.py and uses BIGINT keys (Django DEFAULT_AUTO_FIELD = BigAutoField)

-- NOTE: Your Django is configured to use database 'wtest' on port 3307.
-- If the DB doesn't exist, you can create it first:
-- CREATE DATABASE IF NOT EXISTS wtest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wtest;

-- Ensure session is using utf8mb4 and disable FK checks during import so missing referenced tables (e.g., auth_user)
-- do not stop the whole import. Re-enabled at the end of the script.
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Table: wtestapp_customuser
CREATE TABLE IF NOT EXISTS wtestapp_customuser (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(15) NOT NULL,
  name VARCHAR(100) NOT NULL,
  mobile VARCHAR(15) NOT NULL,
  role VARCHAR(10) NULL,
  otp VARCHAR(6) NULL,
  otp_created_at DATETIME(6) NULL,
  is_verified TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  UNIQUE KEY uq_customuser_username (username),
  UNIQUE KEY uq_customuser_mobile (mobile)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_otpverification
CREATE TABLE IF NOT EXISTS wtestapp_otpverification (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  phone_number VARCHAR(15) NOT NULL,
  otp VARCHAR(6) NOT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  is_verified TINYINT(1) NOT NULL DEFAULT 0,
  attempts INT NOT NULL DEFAULT 0,
  UNIQUE KEY uq_otpverification_phone (phone_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_doctor
-- user_id usually references auth_user(id); removing FK here to avoid import failure if auth_user doesn't exist yet.
-- You can add the FK later via ALTER TABLE once Django migrations create auth_user in the same DB.
CREATE TABLE IF NOT EXISTS wtestapp_doctor (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NULL,
  custom_user_id BIGINT NULL,
  mobile VARCHAR(15) NULL,
  first_name VARCHAR(120) NOT NULL DEFAULT '',
  last_name VARCHAR(120) NOT NULL DEFAULT '',
  email VARCHAR(254) NOT NULL DEFAULT '',
  portal_type VARCHAR(10) NULL,
  gender VARCHAR(10) NULL,
  address LONGTEXT NOT NULL,
  state VARCHAR(50) NOT NULL DEFAULT '',
  city VARCHAR(50) NOT NULL DEFAULT '',
  pincode VARCHAR(10) NOT NULL DEFAULT '',
  date_of_birth DATE NULL,
  profession VARCHAR(80) NOT NULL DEFAULT '',
  specialty VARCHAR(80) NULL,
  contact_info VARCHAR(200) NULL,
  degree VARCHAR(80) NOT NULL DEFAULT '',
  medical_degree VARCHAR(80) NOT NULL DEFAULT '',
  experience INT NULL,
  registration_number VARCHAR(80) NOT NULL DEFAULT '',
  diploma VARCHAR(80) NOT NULL DEFAULT '',
  pg_degree VARCHAR(80) NOT NULL DEFAULT '',
  diplomate VARCHAR(80) NOT NULL DEFAULT '',
  superspeciality VARCHAR(80) NOT NULL DEFAULT '',
  mci_registration VARCHAR(80) NOT NULL DEFAULT '',
  pan VARCHAR(20) NOT NULL DEFAULT '',
  pan_copy VARCHAR(100) NULL,
  cancelled_cheque VARCHAR(100) NULL,
  visiting_card VARCHAR(100) NULL,
  optional_document VARCHAR(100) NULL,
  prescription_name VARCHAR(150) NOT NULL DEFAULT '',
  prescription_file VARCHAR(100) NULL,
  clinic_name VARCHAR(120) NOT NULL DEFAULT '',
  qualification VARCHAR(120) NOT NULL DEFAULT '',
  gst_number VARCHAR(15) NULL,
  has_gst TINYINT(1) NOT NULL DEFAULT 0,
  gst_certificate VARCHAR(100) NULL,
  bank_account_name VARCHAR(120) NULL,
  bank_name VARCHAR(120) NULL,
  account_no VARCHAR(50) NULL,
  branch VARCHAR(100) NULL,
  ifsc VARCHAR(20) NULL,
  agreement_accepted TINYINT(1) NOT NULL DEFAULT 0,
  agreement_amount INT NULL,
  territory VARCHAR(200) NULL,
  emp1_name VARCHAR(150) NULL,
  emp1_mobile VARCHAR(15) NULL,
  emp2_name VARCHAR(150) NULL,
  emp2_mobile VARCHAR(15) NULL,
  designation VARCHAR(50) NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  UNIQUE KEY uq_doctor_mobile (mobile),
  UNIQUE KEY uq_doctor_user (user_id),
  UNIQUE KEY uq_doctor_custom_user (custom_user_id),
  CONSTRAINT fk_doctor_custom_user FOREIGN KEY (custom_user_id) REFERENCES wtestapp_customuser (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_survey
CREATE TABLE IF NOT EXISTS wtestapp_survey (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description LONGTEXT NULL,
  survey_json VARCHAR(100) NULL,
  portal_type VARCHAR(10) NULL,
  amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Auto M2M table for Survey.assigned_to (Survey <-> Doctor)
-- Django's default M2M table typically has no separate id column
CREATE TABLE IF NOT EXISTS wtestapp_survey_assigned_to (
  survey_id BIGINT NOT NULL,
  doctor_id BIGINT NOT NULL,
  UNIQUE KEY uq_survey_doctor (survey_id, doctor_id),
  KEY idx_assigned_to_survey (survey_id),
  KEY idx_assigned_to_doctor (doctor_id),
  CONSTRAINT fk_assigned_to_survey FOREIGN KEY (survey_id) REFERENCES wtestapp_survey (id) ON DELETE CASCADE,
  CONSTRAINT fk_assigned_to_doctor FOREIGN KEY (doctor_id) REFERENCES wtestapp_doctor (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_agreement
CREATE TABLE IF NOT EXISTS wtestapp_agreement (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  doctor_id BIGINT NOT NULL,
  agreement_text LONGTEXT NULL,
  digital_signature LONGTEXT NULL,
  signature_type VARCHAR(20) NOT NULL DEFAULT 'drawn',
  signed_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  pdf_file VARCHAR(100) NULL,
  ip_address VARCHAR(39) NULL,
  user_agent LONGTEXT NULL,
  survey_id BIGINT NULL,
  amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  UNIQUE KEY uq_agreement_doctor (doctor_id),
  KEY idx_agreement_survey (survey_id),
  CONSTRAINT fk_agreement_doctor FOREIGN KEY (doctor_id) REFERENCES wtestapp_doctor (id) ON DELETE CASCADE,
  CONSTRAINT fk_agreement_survey FOREIGN KEY (survey_id) REFERENCES wtestapp_survey (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_question
CREATE TABLE IF NOT EXISTS wtestapp_question (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  survey_id BIGINT NOT NULL,
  question_text VARCHAR(500) NOT NULL,
  question_type VARCHAR(15) NOT NULL DEFAULT 'text',
  options JSON NULL,
  is_required TINYINT(1) NOT NULL DEFAULT 1,
  `order` INT NOT NULL DEFAULT 0,
  help_text VARCHAR(200) NULL,
  KEY idx_question_survey (survey_id),
  CONSTRAINT fk_question_survey FOREIGN KEY (survey_id) REFERENCES wtestapp_survey (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_surveyresponse
CREATE TABLE IF NOT EXISTS wtestapp_surveyresponse (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  doctor_id BIGINT NOT NULL,
  survey_id BIGINT NOT NULL,
  started_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  completed_at DATETIME(6) NULL,
  is_completed TINYINT(1) NOT NULL DEFAULT 0,
  pdf_file VARCHAR(100) NULL,
  UNIQUE KEY uq_response_doctor_survey (doctor_id, survey_id),
  KEY idx_response_doctor (doctor_id),
  KEY idx_response_survey (survey_id),
  CONSTRAINT fk_response_doctor FOREIGN KEY (doctor_id) REFERENCES wtestapp_doctor (id) ON DELETE CASCADE,
  CONSTRAINT fk_response_survey FOREIGN KEY (survey_id) REFERENCES wtestapp_survey (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_answer
CREATE TABLE IF NOT EXISTS wtestapp_answer (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  survey_response_id BIGINT NULL,
  question_id BIGINT NOT NULL,
  answer_text LONGTEXT NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  KEY idx_answer_response (survey_response_id),
  KEY idx_answer_question (question_id),
  CONSTRAINT fk_answer_response FOREIGN KEY (survey_response_id) REFERENCES wtestapp_surveyresponse (id) ON DELETE CASCADE,
  CONSTRAINT fk_answer_question FOREIGN KEY (question_id) REFERENCES wtestapp_question (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_surveyassignment
CREATE TABLE IF NOT EXISTS wtestapp_surveyassignment (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  doctor_id BIGINT NOT NULL,
  survey_id BIGINT NOT NULL,
  assigned_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  UNIQUE KEY uq_assignment_doctor_survey (doctor_id, survey_id),
  KEY idx_assignment_doctor (doctor_id),
  KEY idx_assignment_survey (survey_id),
  CONSTRAINT fk_assignment_doctor FOREIGN KEY (doctor_id) REFERENCES wtestapp_doctor (id) ON DELETE CASCADE,
  CONSTRAINT fk_assignment_survey FOREIGN KEY (survey_id) REFERENCES wtestapp_survey (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: wtestapp_doctorexcelupload
CREATE TABLE IF NOT EXISTS wtestapp_doctorexcelupload (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  excel_file VARCHAR(100) NOT NULL,
  survey_json VARCHAR(100) NULL,
  uploaded_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Re-enable FK checks after all tables are created
SET FOREIGN_KEY_CHECKS = 1;

-- Optional: after running Django migrations (auth_user created) on the SAME DB instance,
-- re-add the foreign key from wtestapp_doctor.user_id to auth_user.id if desired.
-- Make sure auth_user.id and wtestapp_doctor.user_id have the same type (BIGINT) and signedness.
-- Example:
-- ALTER TABLE wtestapp_doctor
--   ADD CONSTRAINT fk_doctor_user FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE;

-- Example inserts (optional): create a survey and add JSON questions
-- INSERT INTO wtestapp_survey (title, description, portal_type, amount)
-- VALUES ('Auto Imported Survey', 'Sample survey created via SQL', 'GC', 500.00);
-- SET @survey_id = LAST_INSERT_ID();
-- INSERT INTO wtestapp_question (survey_id, question_text, question_type, options, is_required, `order`)
-- VALUES (@survey_id, 'What is your preferred brand?', 'radio', JSON_ARRAY('Brand A', 'Brand B', 'Brand C'), 1, 1);
-- INSERT INTO wtestapp_question (survey_id, question_text, question_type, options, is_required, `order`)
-- VALUES (@survey_id, 'Which symptoms do you commonly treat?', 'checkbox', JSON_ARRAY('Acne', 'Pigmentation', 'Aging', 'Rosacea'), 1, 2);
-- INSERT INTO wtestapp_question (survey_id, question_text, question_type, options, is_required, `order`)
-- VALUES (@survey_id, 'Any other comments?', 'text', NULL, 0, 3);
