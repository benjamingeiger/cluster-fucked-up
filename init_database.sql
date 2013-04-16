

CREATE TABLE subreddits (
	name		VARCHAR(50)	PRIMARY KEY
);

CREATE TABLE users (
	name		VARCHAR(50)	PRIMARY KEY
);

CREATE TABLE submissions (
	submission_id	VARCHAR(10)	PRIMARY KEY,
	user_name	VARCHAR(50)	NOT NULL,
	subreddit_name	VARCHAR(50)	NOT NULL,

	title		VARCHAR(255),
	karma		INTEGER,

	link		VARCHAR(255),

	FOREIGN KEY (user_name) REFERENCES users(name),
	FOREIGN KEY (subreddit_name) REFERENCES subreddits(name)
);

CREATE TABLE comments (
	comment_id	VARCHAR(10)	PRIMARY KEY,
	user_name	VARCHAR(50)	NOT NULL,
	submission_id	VARCHAR(10),

	karma		INTEGER,

	FOREIGN KEY (user_name) REFERENCES users(name),
	FOREIGN KEY (submission_id) REFERENCES submissions(submission_id)
);
