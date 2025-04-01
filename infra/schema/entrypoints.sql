CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS entrypoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    show_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (show_id) REFERENCES shows(id),
);