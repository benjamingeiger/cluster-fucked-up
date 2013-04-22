from __future__ import print_function

import sqlite3

import graph


LINK_KARMA_WEIGHT = 10
COMMENT_KARMA_WEIGHT = 1
CROSSPOST_KARMA_WEIGHT = 5

REDDIT_DB = "../reddit.db"
GRAPH_DB = "../graph.db"


def subreddit_score(other_subreddit_name, this_subreddit_name, reddit_db_name):

    conn = sqlite3.connect(reddit_db_name)

    common_posters = graph.find_link_redditors_in_common(other_subreddit_name, this_subreddit_name, conn)

    common_commenters = graph.find_comment_redditors_in_common(other_subreddit_name, this_subreddit_name, conn)

    link_score = 0
    for p in common_posters:
        link_score += (LINK_KARMA_WEIGHT * graph.redditor_subreddit_link_karma(p, this_subreddit_name, conn))

    comment_score = 0
    for c in common_commenters:
        comment_score += (COMMENT_KARMA_WEIGHT * graph.redditor_subreddit_comment_karma(c, this_subreddit_name, conn))

    crosspost_score = (CROSSPOST_KARMA_WEIGHT * graph.subreddit_crosspost_karma(other_subreddit_name, this_subreddit_name, conn))

    return (link_score + comment_score + crosspost_score)
