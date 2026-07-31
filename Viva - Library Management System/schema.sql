CREATE DATABASE IF NOT EXISTS library_manager_db;
USE library_manager_db;

CREATE TABLE IF NOT EXISTS Books (
    Book_id INT AUTO_INCREMENT PRIMARY KEY,
    book_name VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    tot_copies INT NOT NULL DEFAULT 1,
    remaining_copies INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Customer (
    cust_id INT AUTO_INCREMENT PRIMARY KEY,
    cust_name VARCHAR(255) NOT NULL,
    issued_books INT NOT NULL DEFAULT 0,
    Fees_paid DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);
