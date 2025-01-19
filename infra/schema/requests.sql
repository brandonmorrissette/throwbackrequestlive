CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL,
    request_time TIMESTAMP DEFAULT NOW(),
    request_id TEXT NOT NULL,
    show_id INTEGER NOT NULL
);
