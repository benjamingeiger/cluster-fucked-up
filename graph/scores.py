from __future__ import print_function

import sqlite3

from os.path import exists, isfile
from time import sleep
import sys

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
        WHERE last_processed > 0
        ORDER BY last_processed ASC;
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

    link_scores = graph.subreddit_link_karma(common_posters, this_subreddit_name, reddit_conn)
    link_score = LINK_KARMA_WEIGHT * sum(link_scores.values())
    #link_score = 0

    comment_scores = graph.subreddit_comment_karma(common_commenters, this_subreddit_name, reddit_conn)
    comment_score = COMMENT_KARMA_WEIGHT * sum(comment_scores.values())
    #comment_score = 0

    crosspost_score = (CROSSPOST_KARMA_WEIGHT * graph.subreddit_crosspost_karma(other_subreddit_name, this_subreddit_name, reddit_conn))
    #crosspost_score = 0

    return (link_score + comment_score + crosspost_score)


def get_processed_subreddits(reddit_conn):
    cur = reddit_conn.execute(get_processed_subreddits_sql)

    data = cur.fetchall()
    results = [sr for (sr,) in data]

    return results


def cross_subreddit(reddit_db_name, evidence_subreddit_name, output_file_name):
    reddit_conn = sqlite3.connect(reddit_db_name)

    output_file = None
    if not exists(output_file_name) and not isfile(output_file_name):
        try:
            output_file = open(output_file_name, "w")
        except IOError:
            print("Could not open {}".format(output_file_name), file=sys.stderr)
            return
    else:
        return

    subreddits = get_processed_subreddits(reddit_conn)

    for assertion in subreddits:
        if evidence_subreddit_name != assertion:
            score = compute_subreddit_score(evidence_subreddit_name, assertion, reddit_conn)
            print("{},{},{}".format(evidence_subreddit_name, assertion, score), file=output_file)
            print("{},{},{}".format(evidence_subreddit_name, assertion, score))



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

def main():
    reddit_db_name = "../reddit.db"
    reddit_conn = sqlite3.connect(reddit_db_name)
    subreddits = get_processed_subreddits(reddit_conn)

    for subreddit in subreddits:
        output_file_name = "output/{}.csv".format(subreddit)
        if not exists(output_file_name) and not isfile(output_file_name):
            cross_subreddit(reddit_db_name, subreddit, output_file_name)
        sleep(0.5)


if __name__ == "__main__":
    main()
