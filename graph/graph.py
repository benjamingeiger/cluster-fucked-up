from __future__ import print_function

LINK_KARMA_WEIGHT = 10
COMMENT_KARMA_WEIGHT = 1
CROSSPOST_KARMA_WEIGHT = 5


REDDIT_DB = "../reddit.db"
GRAPH_DB = "../graph.db"


######################################################################
# SQL

get_redditor_subreddit_link_karma_sql = \
        """
        SELECT SUM(submissions.karma)
        FROM submissions
        WHERE redditor_name = ?
        AND subreddit_name = ?;
        """

get_redditor_subreddit_comment_karma_sql = \
        """
        SELECT SUM(c.karma)
        FROM (SELECT *
              FROM comments
              WHERE redditor_name = ?) AS c
             INNER JOIN
             (SELECT *
              FROM submissions
              WHERE subreddit_name = ?) AS s
             ON s.submission_id = c.submission_id;
        """

get_subreddit_crosspost_link_karma_sql = \
        """
        SELECT (s2.karma)
        FROM
            (SELECT *
            FROM submissions
            WHERE link != 'self'
            AND subreddit_name = ?
            AND karma > 0) AS s1
            INNER JOIN
            (SELECT *
            FROM submissions
            WHERE link != 'self'
            AND subreddit_name = ?) AS s2
            ON s1.link = s2.link;
        """

######################################################################


def redditor_subreddit_link_karma(
        redditor_name,
        subreddit_name,
        reddit_db):

    cur = reddit_db.execute(get_redditor_subreddit_link_karma_sql,
            (redditor_name.lower(), subreddit_name.lower()))

    karma = cur.fetchone()
    if karma is not None:
        (karma,) = karma
    else:
        karma = 0

    return karma


def redditor_subreddit_comment_karma(
        redditor_name,
        subreddit_name,
        reddit_db):

    cur = reddit_db.execute(get_redditor_subreddit_comment_karma_sql,
            (redditor_name.lower(), subreddit_name.lower()))

    karma = cur.fetchone()
    if karma is not None:
        (karma,) = karma
    else:
        karma = 0

    return karma


def subreddit_crosspost_karma(
        other_subreddit_name,
        this_subreddit_name,
        reddit_db):

    cur = reddit_db.execute(get_subreddit_crosspost_link_karma_sql,
            (other_subreddit_name.lower(), this_subreddit_name.lower()))

    karma = cur.fetchone()
    if karma is not None:
        (karma,) = karma
    else:
        karma = 0

    return karma
