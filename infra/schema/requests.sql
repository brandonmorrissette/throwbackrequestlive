CREATE TABLE IF NOT EXISTS requests (
    id UUID PRIMARY KEY,
    song_id INTEGER NOT NULL,
    request_time TIMESTAMP DEFAULT NOW(),
    show_id INTEGER NOT NULL,
    FOREIGN KEY (song_id) REFERENCES songs(id),
    FOREIGN KEY (show_id) REFERENCES shows(id)
);
