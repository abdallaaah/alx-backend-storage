-- create table and enum field 

CREATE TABLE IF NOT EXISTS users (
	id INT AUTO_INCREMENT NOT NULL,
	email VARCHAR(255) UNIQUE NOT NULL,
	name VARCHAR(255),
	country ENUM('US','CO','TN') NOT NULL,
	PRIMARY KEY(id) 
)
