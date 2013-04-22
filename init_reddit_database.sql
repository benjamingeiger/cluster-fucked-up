CREATE TABLE meta (
	attribute	TEXT	PRIMARY KEY,
	value		TEXT
);

CREATE TABLE subreddits (
	name		TEXT	PRIMARY KEY,
	is_nsfw		INTEGER	DEFAULT 0,
	refs		INTEGER	DEFAULT 0,
	last_processed	INTEGER
);

CREATE TABLE redditors (
	name		TEXT	PRIMARY KEY,
	refs		INTEGER	DEFAULT 0,
	last_processed	INTEGER
);

CREATE TABLE submissions (
	submission_id	TEXT	PRIMARY KEY,
	redditor_name	TEXT	NOT NULL,
	subreddit_name	TEXT	NOT NULL,

	title		TEXT,
	karma		INTEGER,

	link		TEXT,
	is_nsfw		INTEGER DEFAULT 0,

	FOREIGN KEY (redditor_name) REFERENCES redditors(name),
	FOREIGN KEY (subreddit_name) REFERENCES subreddits(name)
);

CREATE TABLE comments (
	comment_id	TEXT	PRIMARY KEY,
	redditor_name	TEXT	NOT NULL,
	submission_id	TEXT,

	karma		INTEGER,

	FOREIGN KEY (redditor_name) REFERENCES redditors(name),
	FOREIGN KEY (submission_id) REFERENCES submissions(submission_id)
);
