
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_date TIMESTAMP NOT NULL,
    command_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tweet_id INTEGER NOT NULL,
    reply_count INTEGER,
    retweet_count INTEGER,
    lang TEXT,
    user_name TEXT NOT NULL,
    content TEXT NOT NULL,
    likes INTEGER
);