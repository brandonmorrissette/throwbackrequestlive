CREATE TABLE IF NOT EXISTS submissions (
    id UUID NOT NULL,
    entrypoint_id UUID NOT NULL,
    FOREIGN KEY (id) REFERENCES requests(id),
    FOREIGN KEY (entrypoint_id) REFERENCES entrypoints(id),
    UNIQUE (id, entrypoint_id)
);