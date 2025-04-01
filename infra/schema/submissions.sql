CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    uid TEXT NOT NULL UNIQUE,
    entrypoint_id UUID NOT NULL,
    FOREIGN KEY (uid) REFERENCES requests(request_id),
    UNIQUE (request_id, entry_id)
);
