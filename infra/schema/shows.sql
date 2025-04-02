CREATE TABLE IF NOT EXISTS shows (
    id SERIAL PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    name VARCHAR(255) NOT NULL,
    venue VARCHAR(255),
    street VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255)
);