CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    band_name VARCHAR(255) NOT NULL,
    song_name VARCHAR(255) NOT NULL,
    total_requests INTEGER DEFAULT 0,
    requests_per_show INTEGER DEFAULT 0
);
