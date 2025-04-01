CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    uid TEXT NOT NULL,
    entrypoint_id UUID NOT NULL,
    FOREIGN KEY (entrypoint_id) REFERENCES entrypoints(id),
    FOREIGN KEY (uid) REFERENCES requests(id),
    UNIQUE (request_id, entry_id)
);
