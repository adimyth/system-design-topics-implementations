-- Create the employee table
CREATE TABLE employee (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    department VARCHAR(50),
    location VARCHAR(50)
);

-- Create indexes on department and location
CREATE INDEX idx_department ON employee(department);

CREATE INDEX idx_location ON employee(location);

-- Function to generate random names
CREATE
OR REPLACE FUNCTION random_name() RETURNS VARCHAR(100) AS $ $ DECLARE first_names VARCHAR [] := ARRAY ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa', 'William', 'Elizabeth'];

last_names VARCHAR [] := ARRAY ['Smith', 'Johnson', 'Brown', 'Taylor', 'Miller', 'Wilson', 'Moore', 'Anderson', 'Jackson', 'White'];

BEGIN RETURN first_names [floor(random() * 10 + 1)] || ' ' || last_names [floor(random() * 10 + 1)];

END;

$ $ LANGUAGE plpgsql;

-- Function to generate random department
CREATE
OR REPLACE FUNCTION random_department() RETURNS VARCHAR(50) AS $ $ DECLARE departments VARCHAR [] := ARRAY ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations', 'Customer Support', 'Legal', 'Research', 'IT'];

BEGIN RETURN departments [floor(random() * 10 + 1)];

END;

$ $ LANGUAGE plpgsql;

-- Function to generate random location
CREATE
OR REPLACE FUNCTION random_location() RETURNS VARCHAR(50) AS $ $ DECLARE locations VARCHAR [] := ARRAY ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'];

BEGIN RETURN locations [floor(random() * 10 + 1)];

END;

$ $ LANGUAGE plpgsql;

-- Insert 10 million records
INSERT INTO
    employee (name, age, department, location)
SELECT
    random_name(),
    floor(random() * (65 - 20 + 1) + 20) :: int,
    random_department(),
    random_location()
FROM
    generate_series(1, 10000000);