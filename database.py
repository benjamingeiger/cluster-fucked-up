from __future__ import print_function

import praw
import sqlite3

from calendar import timegm
from datetime import datetime

from collections import Counter

#from utilities import debug

import reddit

from definitions import USER_AGENT

######################################################################

# SQL statements we'll need
insert_redditor_sql = \
"""
INSERT OR REPLACE INTO redditors
(name, refs, last_processed)
VALUES (?, ?, ?);
"""

insert_subreddit_sql = \
"""
INSERT OR REPLACE INTO subreddits
(name, refs, last_processed)
VALUES (?, ?, ?);
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


def get_refs_for_redditors(redditor_names, conn):
    num_redditors = len(redditor_names)
    get_redditors_sql = \
            """
            SELECT name, refs
            FROM redditors
            WHERE last_processed IS NULL OR last_processed < 0
            AND name IN ({});
            """.format(",".join(["?"] * num_redditors))

    print(get_redditors_sql)

    cur = conn.execute(get_redditors_sql, redditor_names)

    return {u[0]: u[1] for u in cur.fetchall()}


def process_subreddit(subreddit_name,
                      database_name,
                      limit=1000,
                      reddit_obj=None):

    if reddit_obj is None:
        reddit_obj = praw.Reddit(USER_AGENT)

    submission_gen = reddit.get_hot_from_subreddit(subreddit_name,
                                                   reddit_obj=reddit_obj,
                                                   limit=limit)

    redditors = {}
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

        redditors[redditor_name] = redditors.get(redditor_name, 0) + 1

        submissions.append((submission_id, redditor_name, subreddit_name,
                            title, karma, link))

        for c in reddit.get_all_comments_from_submission(s, limit=limit):
            if c.author is None:
                # Deleted comment.
                continue

            comment_id = c.name
            redditor_name = c.author.name
            karma = c.score

            redditors[redditor_name] = redditors.get(redditor_name, 0) + 1

            comments.append((comment_id, redditor_name, submission_id, karma))

    # Add up the refs.
    conn = sqlite3.connect(database_name)

    refs = get_refs_for_redditors(redditors.keys(), conn)
    redditors = Counter(redditors) + Counter(refs)

    timestamp = timegm(datetime.utcnow().utctimetuple())
    redditors = [(u, redditors[u], None) for u in redditors.keys()]

    cur = conn.cursor()

    cur.executemany(insert_redditor_sql, redditors)
    cur.executemany(insert_submission_sql, submissions)
    cur.executemany(insert_comment_sql, comments)

    cur.executemany(insert_subreddit_sql, [(subreddit_name, -1, timestamp)])

    conn.commit()
