CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS shows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    name VARCHAR(255) NOT NULL,
    venue VARCHAR(255),
    street VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255),
    entry_point_id UUID NOT NULL UNIQUE,
    FOREIGN KEY (entry_point_id) REFERENCES entrypoints(id)
);