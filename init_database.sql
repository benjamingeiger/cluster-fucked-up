

CREATE TABLE subreddits (
	name		TEXT	PRIMARY KEY,
	last_processed	INTEGER
);

CREATE TABLE users (
	name		TEXT	PRIMARY KEY,
	last_processed	INTEGER
);

CREATE TABLE submissions (
	submission_id	TEXT	PRIMARY KEY,
	user_name	TEXT	NOT NULL,
	subreddit_name	TEXT	NOT NULL,

	title		TEXT,
	karma		INTEGER,

	link		TEXT,

	FOREIGN KEY (user_name) REFERENCES users(name),
	FOREIGN KEY (subreddit_name) REFERENCES subreddits(name)
);

CREATE TABLE comments (
	comment_id	TEXT	PRIMARY KEY,
	user_name	TEXT	NOT NULL,
	submission_id	TEXT,

	karma		INTEGER,

	FOREIGN KEY (user_name) REFERENCES users(name),
	FOREIGN KEY (submission_id) REFERENCES submissions(submission_id)
);
