CREATE TABLE IF NOT EXISTS SubscriptionRelations (
    relation_id INTEGER PRIMARY KEY,
    subscriber_id INTEGER,
    subscription_id INTEGER,
    FOREIGN KEY (subscriber_id) REFERENCES Subscribers (subscriber_id),
    FOREIGN KEY (subscription_id) REFERENCES Subscriptions (subscription_id)
    CONSTRAINT unique_relation_id UNIQUE (subscriber_id, subscription_id)
);