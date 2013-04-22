CREATE TABLE meta (
	attribute	TEXT	PRIMARY KEY,
	value		TEXT
);

CREATE TABLE subreddit_scores (
	evidence	TEXT,
	assertion	TEXT,
	score		INTEGER,

	PRIMARY KEY (evidence, assertion)
);
