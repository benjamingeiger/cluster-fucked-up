from __future__ import print_function

import praw
import sqlite3

from calendar import timegm
from datetime import datetime

from collections import Counter

from utilities import debug_silence as debug

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

update_redditor_refs_sql = \
"""
UPDATE redditors
SET refs = ?
WHERE name = ?;
"""

insert_subreddit_sql = \
"""
INSERT OR REPLACE INTO subreddits
(name, is_nsfw, refs, last_processed)
VALUES (?, ?, ?, ?);
"""

update_subreddit_refs_sql = \
"""
UPDATE subreddits
SET refs = ?
WHERE name = ?;
"""

insert_submission_sql = \
"""
INSERT OR REPLACE INTO submissions
(submission_id, redditor_name, subreddit_name,
 title, karma, link, is_nsfw)
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

insert_comment_sql = \
"""
INSERT OR REPLACE INTO comments
(comment_id, redditor_name, submission_id, karma)
VALUES (?, ?, ?, ?);
"""

find_subreddit_sql = \
"""
SELECT name
FROM subreddits
WHERE last_processed IS NULL OR last_processed <= 0
ORDER BY refs DESC
LIMIT 1
"""

find_redditor_sql = \
"""
SELECT name
FROM redditors
WHERE last_processed IS NULL OR last_processed <= 0
ORDER BY refs DESC
LIMIT 1
"""

mark_seeded_sql = \
"""
INSERT OR REPLACE INTO meta
(attribute, value)
VALUES ('seeded', 'true');
"""

check_seeded_sql = \
"""
SELECT value
FROM meta
WHERE attribute = 'seeded';
"""

count_subreddits_processed_sql = \
"""
SELECT COUNT(*)
FROM subreddits
WHERE last_processed > 0;
"""

is_subreddit_processed_sql = \
"""
SELECT *
FROM subreddits
WHERE name = ?
AND last_processed > 0;
"""

mark_redditor_processed_sql = \
"""
UPDATE redditors
SET last_processed = ?
WHERE name = ?;
"""

mark_subreddit_processed_sql = \
"""
UPDATE subreddits
SET last_processed = ?
WHERE name = ?;
"""

######################################################################


def get_refs_for_redditors(redditor_names, conn):
    if len(redditor_names) <= 900:
        return get_refs_for_redditors_helper(redditor_names, conn)

    results1 = get_refs_for_redditors_helper(redditor_names[:900], conn)
    results2 = get_refs_for_redditors(redditor_names[900:], conn)

    results1.update(results2)
    return results1


def get_refs_for_redditors_helper(redditor_names, conn):
    num_redditors = len(redditor_names)
    get_redditors_sql = \
            """
            SELECT name, refs
            FROM redditors
            WHERE name IN ({});
            """.format(",".join(["?"] * num_redditors))

    cur = conn.execute(get_redditors_sql, redditor_names)

    return {u[0]: u[1] for u in cur.fetchall()}


def get_refs_for_subreddits(subreddit_names, conn):
    if len(subreddit_names) <= 900:
        return get_refs_for_subreddits_helper(subreddit_names, conn)

    results1 = get_refs_for_subreddits_helper(subreddit_names[:900], conn)
    results2 = get_refs_for_subreddits(subreddit_names[900:], conn)

    results1.update(results2)
    return results1


def get_refs_for_subreddits_helper(subreddit_names, conn):
    num_subreddits = len(subreddit_names)
    get_subreddits_sql = \
            """
            SELECT name, refs
            FROM subreddits
            WHERE name IN ({});
            """.format(",".join(["?"] * num_subreddits))

    debug(get_subreddits_sql)
    debug(subreddit_names)

    cur = conn.execute(get_subreddits_sql, subreddit_names)

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

    count = 0

    for s in submission_gen:
        if (limit < 100) or (count % (limit / 10) == 0):
            print("    -> processing submission number", count)
        submission_id = s.name
        try:
            redditor_name = s.author.name.lower()
        except AttributeError:
            redditor_name = ""
        title = s.title
        karma = s.score
        if s.is_self:
            link = "self"
        else:
            link = s.url
        is_nsfw = 1 if s.over_18 else 0

        if redditor_name != "":
            redditors[redditor_name] = redditors.get(redditor_name, 0) + 10

            submissions.append((submission_id, redditor_name, subreddit_name,
                                title, karma, link, is_nsfw))

        for c in reddit.get_all_comments_from_submission(s, limit=5):
            if c.author is None:
                # Deleted comment.
                continue

            comment_id = c.name
            try:
                redditor_name = c.author.name.lower()
            except AttributeError:
                continue
            karma = c.score

            redditors[redditor_name] = redditors.get(redditor_name, 0) + 1

            comments.append((comment_id, redditor_name, submission_id, karma))

        count += 1

    # Add up the refs.
    conn = sqlite3.connect(database_name)

    refs = get_refs_for_redditors(redditors.keys(), conn)
    new_redditors = {x: redditors[x]
                     for x in redditors
                     if x not in refs}
    old_redditors = {x: redditors[x]
                     for x in redditors
                     if x in refs}
    old_redditors = Counter(old_redditors) + Counter(refs)

    timestamp = timegm(datetime.utcnow().utctimetuple())
    old_redditors = [(old_redditors[u], u) for u in old_redditors.keys()]
    new_redditors = [(u, new_redditors[u], None) for u in new_redditors.keys()]

    debug("old:", old_redditors)
    debug("new:", new_redditors)

    cur = conn.cursor()

    cur.executemany(insert_redditor_sql, new_redditors)
    cur.executemany(update_redditor_refs_sql, old_redditors)
    cur.executemany(insert_submission_sql, submissions)
    cur.executemany(insert_comment_sql, comments)

    subreddit_is_nsfw = reddit_obj.get_subreddit(subreddit_name).over18
    subreddit_is_nsfw = 1 if subreddit_is_nsfw else 0

    cur.executemany(insert_subreddit_sql,
                    [(subreddit_name, subreddit_is_nsfw, -1, timestamp)])

    conn.commit()


# holy shit this is ugly, but we can't initialize a subreddit object
# for every single comment that comes through. so we cache.
subreddit_display_names = {}


def process_redditor(redditor_name,
                     database_name,
                     limit=1000,
                     reddit_obj=None):

    if reddit_obj is None:
        reddit_obj = praw.Reddit(USER_AGENT)

    debug("Got reddit object")

    submission_gen = reddit.get_submissions_from_redditor(
                                redditor_name,
                                reddit_obj=reddit_obj,
                                limit=limit)
    comment_gen = reddit.get_comments_from_redditor(
                                redditor_name,
                                reddit_obj=reddit_obj,
                                limit=limit)

    debug("Got submissions and comments")

    subreddits = {}
    submissions = []
    comments = []

    for s in submission_gen:
        submission_id = s.name
        subreddit_name = s.subreddit.display_name.lower()
        title = s.title
        karma = s.score
        if s.is_self:
            link = "self"
        else:
            link = s.url
        is_nsfw = 1 if s.over_18 else 0

        subreddits[subreddit_name] = subreddits.get(subreddit_name, 0) + 10

        submissions.append((submission_id, redditor_name, subreddit_name,
                            title, karma, link, is_nsfw))

    for c in comment_gen:
        if c.author is None:
            # Deleted comment.
            continue

        comment_id = c.name
        submission_id = c.parent_id
        karma = c.score

        if c.subreddit_id in subreddit_display_names:
            subreddit_name = subreddit_display_names[c.subreddit_id]
        else:
            try:
                subreddit_name = c.subreddit.display_name.lower()
                subreddit_display_names[c.subreddit_id] = subreddit_name
            except ValueError:
                subreddit_name = None

        if subreddit_name:
            subreddits[subreddit_name] = subreddits.get(subreddit_name, 0) + 1

        comments.append((comment_id, redditor_name, submission_id, karma))

    # Add up the refs.
    conn = sqlite3.connect(database_name)

    refs = get_refs_for_subreddits(subreddits.keys(), conn)
    new_subreddits = {x: subreddits[x]
                     for x in subreddits
                     if x not in refs}
    old_subreddits = {x: subreddits[x]
                     for x in subreddits
                     if x in refs}
    old_subreddits = Counter(old_subreddits) + Counter(refs)

    timestamp = timegm(datetime.utcnow().utctimetuple())
    old_subreddits = [(u, old_subreddits[u])
            for u in old_subreddits.keys()]
    new_subreddits = [(u, None, new_subreddits[u], None)
            for u in new_subreddits.keys()]

    debug("Old:", old_subreddits)
    debug("New:", new_subreddits)

    cur = conn.cursor()

    cur.executemany(insert_subreddit_sql, new_subreddits)
    cur.executemany(update_subreddit_refs_sql, old_subreddits)
    cur.executemany(insert_submission_sql, submissions)
    cur.executemany(insert_comment_sql, comments)

    cur.executemany(insert_redditor_sql, [(redditor_name, -1, timestamp)])

    conn.commit()


def find_next_subreddit(database_name):
    conn = sqlite3.connect(database_name)

    cur = conn.execute(find_subreddit_sql)
    data = cur.fetchone()

    if data is not None:
        (data,) = data

    return data


def find_next_redditor(database_name):
    conn = sqlite3.connect(database_name)

    cur = conn.execute(find_redditor_sql)
    data = cur.fetchone()

    if data is not None:
        (data,) = data

    return data


def mark_seeded(database_name):
    conn = sqlite3.connect(database_name)

    conn.execute(mark_seeded_sql)
    conn.commit()


def is_seeded(database_name):
    conn = sqlite3.connect(database_name)

    cur = conn.execute(check_seeded_sql)

    return (cur.fetchone() is not None)


def count_subreddits_processed(database_name):
    conn = sqlite3.connect(database_name)

    cur = conn.execute(count_subreddits_processed_sql)
    (data,) = cur.fetchone()

    return data


def is_subreddit_processed(subreddit_name, database_name):
    conn = sqlite3.connect(database_name)

    cur = conn.execute(is_subreddit_processed_sql, (subreddit_name,))

    return (cur.fetchone() is not None)


def mark_redditor_processed(redditor_name, database_name):
    conn = sqlite3.connect(database_name)

    timestamp = timegm(datetime.utcnow().utctimetuple())
    conn.execute(mark_redditor_processed_sql,
            (timestamp, redditor_name.lower()))
    conn.commit()


def mark_subreddit_processed(subreddit_name, database_name):
    conn = sqlite3.connect(database_name)

    timestamp = timegm(datetime.utcnow().utctimetuple())
    conn.execute(mark_subreddit_processed_sql,
            (timestamp, subreddit_name.lower()))
    conn.commit()
