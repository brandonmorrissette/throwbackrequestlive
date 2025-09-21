CREATE TABLE IF NOT EXISTS requests (
    id UUID NOT NULL PRIMARY KEY,
    show_hash VARCHAR NOT NULL,
    song_code VARCHAR NOT NULL,
    request_time TIMESTAMP DEFAULT NOW(),
);
