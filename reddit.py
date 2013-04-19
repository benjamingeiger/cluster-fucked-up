from __future__ import print_function

import praw

#import sqlite3

from definitions import USER_AGENT


def get_hot_from_subreddit(subreddit_name,
                           limit=1000,
                           reddit_obj=None,
                           print_updates=True):
    """Retrieve the hot submissions from the given subreddit."""

    if reddit_obj is None:
        reddit_obj = praw.Reddit(USER_AGENT)

    subreddit = reddit_obj.get_subreddit(subreddit_name)

    hot_gen = subreddit.get_hot(limit=limit)

    count = 0
    hot = []
    for submission in hot_gen:
        hot.append(submission)
        count += 1
        if print_updates and count % 100 == 0:
            print(count)

    return hot


def get_all_comments_from_submission(submission,
                                     limit=1000,
                                     print_updates=True):
    """Retrieve all comments from the given submission."""

    submission.replace_more_comments(limit=None, threshold=0)

    return submission.comments

def get_submissions_from_redditor(redditor_name,
                                  limit=1000,
                                  reddit_obj=None,
                                  print_updates=True):
    """Retrieve the most recent submissions from the given redditor."""

    if reddit_obj is None:
        reddit_obj = praw.Reddit(USER_AGENT)

    redditor = reddit_obj.get_redditor(redditor_name)

    submissions_gen = redditor.get_submitted(limit=limit)

    count = 0
    submissions = []

    for submission in submissions_gen:
        submissions.append(submission)
        count += 1
        if print_updates and count % 100 == 0:
            print(count)

    return submissions

