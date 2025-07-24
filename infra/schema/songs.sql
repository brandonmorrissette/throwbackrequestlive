CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS songs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    band_name VARCHAR(255) NOT NULL,
    song_name VARCHAR(255) NOT NULL
);
