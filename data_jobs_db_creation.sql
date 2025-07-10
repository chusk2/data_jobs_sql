-- =================================================================
--  SQL Script to Create the Data Jobs Database
-- =================================================================
--  This script is generated based on the normalization performed
--  in the provided Jupyter Notebook.
-- =================================================================

-- Drop the database if it already exists to start with a clean slate
DROP DATABASE IF EXISTS data_jobs;

-- Create the new database
CREATE DATABASE data_jobs;

-- Select the newly created database for use
USE data_jobs;

-- =================================================================
--  Dimension Tables
-- =================================================================

-- Table for storing unique company names
CREATE TABLE companies (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    company VARCHAR(255) UNIQUE
);

-- Table for storing unique countries
CREATE TABLE countries (
    country_id INT PRIMARY KEY AUTO_INCREMENT,
    country VARCHAR(100) NOT NULL UNIQUE
);

-- Table for storing unique job locations
CREATE TABLE locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    location_name VARCHAR(255) NOT NULL UNIQUE
);

-- Table for storing unique job portals (from job_via)
CREATE TABLE job_via (
    job_via_id INT PRIMARY KEY AUTO_INCREMENT,
    job_via VARCHAR(255) NOT NULL UNIQUE
);

-- Table for storing unique job schedule types
CREATE TABLE job_schedules (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    schedule_type VARCHAR(50) NOT NULL UNIQUE
);

-- Table for storing unique job skills
CREATE TABLE skills (
    skill_id INT PRIMARY KEY AUTO_INCREMENT,
    skill VARCHAR(100) NOT NULL UNIQUE
);

-- Table for storing unique short job titles
CREATE TABLE job_titles (
    job_title_id INT PRIMARY KEY AUTO_INCREMENT,
    job_title VARCHAR(100) NOT NULL UNIQUE
);

-- =================================================================
--  Fact Table
-- =================================================================

-- The main table for job postings.
-- Each row represents a job with a specific skill and schedule type.
CREATE TABLE job_postings (
    posting_id INT PRIMARY KEY AUTO_INCREMENT,
    job_title_full VARCHAR(255),
    work_from_home BOOLEAN,
    job_posted_date DATETIME,
    no_degree_mention BOOLEAN,
    health_insurance BOOLEAN,
    salary_rate VARCHAR(20),
    salary_year_avg DECIMAL(12, 2),
    salary_hour_avg DECIMAL(10, 4),

    -- Foreign Keys to Dimension Tables
    company_id INT,
    job_country_id INT,
    search_location_id INT,
    job_location_id INT,
    job_via_id INT,
    schedule_id INT,
    skill_id INT,
    job_title_id INT,

    -- Foreign Key Constraints
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (job_country_id) REFERENCES countries(country_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (search_location_id) REFERENCES countries(country_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (job_location_id) REFERENCES locations(location_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (job_via_id) REFERENCES job_via(job_via_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES job_schedules(schedule_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (job_title_id) REFERENCES job_titles(job_title_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- =================================================================
--  End of Script
-- =================================================================
