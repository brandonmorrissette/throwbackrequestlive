CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL,
    vote_time TIMESTAMP DEFAULT NOW(),
    voter_id TEXT NOT NULL,
    event_id INTEGER NOT NULL
);
