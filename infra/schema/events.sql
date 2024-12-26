CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    datetime TIMESTAMP NOT NULL,
    name VARCHAR(255) NOT NULL,
    venue VARCHAR(255),
    street VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255)
);