CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE,
    entrypoint_id UUID NOT NULL,
    FOREIGN KEY (uuid) REFERENCES requests(request_id),
    UNIQUE (uuid, entry_id)
);
