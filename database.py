from __future__ import print_function

import praw
import sqlite3

from calendar import timegm
from datetime import datetime

from utilities import debug

import reddit

from definitions import USER_AGENT

######################################################################

# SQL statements we'll need
insert_redditor_sql = \
"""
INSERT OR REPLACE INTO redditors
(name, last_processed)
VALUES (?, ?);
"""

insert_subreddit_sql = \
"""
INSERT OR REPLACE INTO subreddits
(name, last_processed)
VALUES (?, ?);
"""

insert_submission_sql = \
"""
INSERT OR REPLACE INTO submissions
(submission_id, redditor_name, subreddit_name,
 title, karma, link)
VALUES (?, ?, ?, ?, ?, ?);
"""

insert_comment_sql = \
"""
INSERT OR REPLACE INTO comments
(comment_id, redditor_name, submission_id, karma)
VALUES (?, ?, ?, ?);
"""

######################################################################


def process_subreddit(subreddit_name,
                      database_name,
                      limit=1000,
                      reddit_obj=None):

    if reddit_obj is None:
        reddit_obj = praw.Reddit(USER_AGENT)

    submission_gen = reddit.get_hot_from_subreddit(subreddit_name,
                                                   reddit_obj=reddit_obj,
                                                   limit=limit)

    redditors = []
    submissions = []
    comments = []

    for s in submission_gen:
        submission_id = s.name
        redditor_name = s.author.name
        title = s.title
        karma = s.score
        if s.is_self:
            link = "self"
        else:
            link = s.url

        if redditor_name not in redditors:
            redditors.append(redditor_name)

        submissions.append((submission_id, redditor_name, subreddit_name,
                            title, karma, link))

        for c in reddit.get_all_comments_from_submission(s, limit=limit):
            if c.author is None:
                # Deleted comment.
                continue

            comment_id = c.name
            redditor_name = c.author.name
            karma = c.score

            if redditor_name not in redditors:
                redditors.append(redditor_name)

            comments.append((comment_id, redditor_name, submission_id, karma))

    timestamp = timegm(datetime.utcnow().utctimetuple())
    redditors = [(u, None) for u in redditors]

    conn = sqlite3.connect(database_name)
    with conn:
        cur = conn.cursor()

        cur.executemany(insert_redditor_sql, redditors)
        cur.executemany(insert_submission_sql, submissions)
        cur.executemany(insert_comment_sql, comments)

        cur.executemany(insert_subreddit_sql, [(subreddit_name, timestamp)])

        conn.commit()
