from __future__ import print_function

import praw

#import sqlite3

from definitions import USER_AGENT


def get_hot_from_subreddit(subreddit_name,
                           limit=1000,
                           reddit=None,
                           print_updates=True):
    """Retrieve the hot submissions from the given subreddit."""

    if reddit is None:
        reddit = praw.Reddit(USER_AGENT)

    subreddit = reddit.get_subreddit(subreddit_name)

    hot_gen = subreddit.get_hot(limit=limit)

    count = 0
    hot = []
    for submission in hot_gen:
        hot.append(submission)
        count += 1
        if print_updates and count % 100 == 0:
            print(count)

    return hot
