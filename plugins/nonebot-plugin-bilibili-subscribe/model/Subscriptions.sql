CREATE TABLE IF NOT EXISTS Subscriptions (
    subscription_id INTEGER PRIMARY KEY,
    name TEXT,
    last_dynamic_id TEXT,
    CONSTRAINT unique_subscription_id UNIQUE (subscription_id)    
);
