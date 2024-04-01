CREATE TABLE IF NOT EXISTS Subscribers (
    subscriber_id INTEGER PRIMARY KEY,
    name TEXT,
    CONSTRAINT unique_subscriber_id UNIQUE (subscriber_id)
);
