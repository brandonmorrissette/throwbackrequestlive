CREATE TABLE IF NOT EXISTS submissions (
    id UUID NOT NULL,
    entrypoint_id UUID NOT NULL,
    FOREIGN KEY (uuid) REFERENCES requests(id),
    FOREIGN KEY (entrypoint_id) REFERENCES entrypoints(id),
    UNIQUE (uuid, entrypoint_id)
);