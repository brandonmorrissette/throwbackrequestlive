CREATE TABLE IF NOT EXISTS request (
    id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL,
    request_time TIMESTAMP DEFAULT NOW(),
    request_id TEXT NOT NULL,
    event_id INTEGER NOT NULL
);
