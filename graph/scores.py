from __future__ import print_function

import sqlite3

import graph


LINK_KARMA_WEIGHT = 10
COMMENT_KARMA_WEIGHT = 1
CROSSPOST_KARMA_WEIGHT = 5

REDDIT_DB = "../reddit.db"
GRAPH_DB = "../graph.db"

######################################################################
# SQL

get_processed_subreddits_sql = \
        """
        SELECT DISTINCT name
        FROM subreddits
        WHERE last_processed > 0;
        """

insert_subreddit_pair_sql = \
        """
        INSERT OR REPLACE INTO subreddit_scores
        (evidence, assertion, score)
        VALUES (?,?,?);
        """

######################################################################


def compute_subreddit_score(other_subreddit_name, this_subreddit_name, reddit_conn):

    common_posters = graph.find_link_redditors_in_common(other_subreddit_name, this_subreddit_name, reddit_conn)

    common_commenters = graph.find_comment_redditors_in_common(other_subreddit_name, this_subreddit_name, reddit_conn)

    link_score = 0
    for p in common_posters:
        link_score += (LINK_KARMA_WEIGHT * graph.redditor_subreddit_link_karma(p, this_subreddit_name, reddit_conn))

    comment_score = 0
    for c in common_commenters:
        comment_score += (COMMENT_KARMA_WEIGHT * graph.redditor_subreddit_comment_karma(c, this_subreddit_name, reddit_conn))

    crosspost_score = (CROSSPOST_KARMA_WEIGHT * graph.subreddit_crosspost_karma(other_subreddit_name, this_subreddit_name, reddit_conn))

    return (link_score + comment_score + crosspost_score)


def get_processed_subreddits(reddit_conn):
    cur = reddit_conn.execute(get_processed_subreddits_sql)

    data = cur.fetchall()
    results = [sr for (sr,) in data]

    return results


def populate_database(reddit_db_name, graph_db_name):
    reddit_conn = sqlite3.connect(reddit_db_name)
    graph_conn = sqlite3.connect(graph_db_name)

    subreddits = sorted(get_processed_subreddits(reddit_conn))

    for evidence in subreddits:
        for assertion in subreddits:
            print("Evidence:", evidence, "Assertion:", assertion)
            if evidence != assertion:
                score = compute_subreddit_score(evidence, assertion, reddit_conn)

                graph_conn.execute(insert_subreddit_pair_sql,
                                   (evidence, assertion, score))
                graph_conn.commit()

