from __future__ import print_function


######################################################################
# SQL

get_common_link_redditors_sql = \
        """
        SELECT DISTINCT redditor_name
        FROM submissions
        WHERE subreddit_name = ?
        INTERSECT
        SELECT DISTINCT redditor_name
        FROM submissions
        WHERE subreddit_name = ?;
        """

get_common_comment_redditors_sql = \
        """
        SELECT DISTINCT c.redditor_name
        FROM submissions s INNER JOIN comments c
             ON s.submission_id = c.submission_id
        WHERE s.subreddit_name = ?
        INTERSECT
        SELECT DISTINCT c.redditor_name
        FROM submissions s INNER JOIN comments c
             ON s.submission_id = c.submission_id
        WHERE s.subreddit_name = ?;
        """

get_subreddit_link_karma_sql = \
        """
        SELECT redditor_name, SUM(submissions.karma)
        FROM submissions
        WHERE subreddit_name = ?
        AND redditor_name IN (SELECT * FROM common_redditors)
        GROUP BY redditor_name;
        """

get_subreddit_comment_karma_sql = \
        """
        SELECT c.redditor_name, SUM(c.karma)
        FROM (SELECT *
              FROM comments
              WHERE redditor_name IN (SELECT * FROM common_redditors)) AS c
             INNER JOIN
             (SELECT *
              FROM submissions
              WHERE subreddit_name = ?) AS s
             ON s.submission_id = c.submission_id
        GROUP BY c.redditor_name;
        """

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


def find_link_redditors_in_common(
        other_subreddit_name,
        this_subreddit_name,
        reddit_db):

    cur = reddit_db.execute(get_common_link_redditors_sql,
            (other_subreddit_name.lower(), this_subreddit_name.lower()))

    data = cur.fetchall()

    results = []
    for item in data:
        results.append(item[0])

    return results


def find_comment_redditors_in_common(
        other_subreddit_name,
        this_subreddit_name,
        reddit_db):

    cur = reddit_db.execute(get_common_comment_redditors_sql,
            (other_subreddit_name.lower(), this_subreddit_name.lower()))

    data = cur.fetchall()

    results = []
    for item in data:
        results.append(item[0])

    return results


def subreddit_link_karma(
        redditor_names,
        subreddit_name,
        reddit_db):

    # prep temp table
    reddit_db.execute(
            """
            CREATE TEMPORARY TABLE common_redditors (
                name TEXT PRIMARY KEY
            );
            """)
    reddit_db.executemany(
            """
            INSERT INTO common_redditors (name)
            VALUES (?);
            """, [(name,) for name in redditor_names])

    cur = reddit_db.execute(get_subreddit_link_karma_sql, (subreddit_name,))
    data = cur.fetchall()

    reddit_db.execute("DROP TABLE common_redditors;")

    if data is None:
        return None
    else:
        return {d[0]:d[1] for d in data}

def subreddit_comment_karma(
        redditor_names,
        subreddit_name,
        reddit_db):

    # prep temp table
    reddit_db.execute(
            """
            CREATE TEMPORARY TABLE common_redditors (
                name TEXT PRIMARY KEY
            );
            """)
    reddit_db.executemany(
            """
            INSERT INTO common_redditors (name)
            VALUES (?);
            """, [(name,) for name in redditor_names])

    cur = reddit_db.execute(get_subreddit_comment_karma_sql, (subreddit_name,))
    data = cur.fetchall()

    reddit_db.execute("DROP TABLE common_redditors;")

    if data is None:
        return None
    else:
        return {d[0]:d[1] for d in data}


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
