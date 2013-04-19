

CREATE TABLE subreddits (
	name		TEXT	PRIMARY KEY,
	last_processed	INTEGER
);

CREATE TABLE redditors (
	name		TEXT	PRIMARY KEY,
	last_processed	INTEGER
);

CREATE TABLE submissions (
	submission_id	TEXT	PRIMARY KEY,
	redditor_name	TEXT	NOT NULL,
	subreddit_name	TEXT	NOT NULL,

	title		TEXT,
	karma		INTEGER,

	link		TEXT,

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
