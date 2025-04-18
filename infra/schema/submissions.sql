CREATE TABLE IF NOT EXISTS submissions (
    id UUID NOT NULL,
    entry_point_id UUID NOT NULL,
    PRIMARY KEY (id, entry_point_id),
    FOREIGN KEY (id) REFERENCES requests(id),
    FOREIGN KEY (entry_point_id) REFERENCES entrypoints(id),
    UNIQUE (id, entry_point_id)
);