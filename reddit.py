from __future__ import print_function

import praw

#import sqlite3

from definitions import USER_AGENT


def unroll_generator(gen, print_updates=True):
    count = 0
    items = []

    for item in gen:
        items.append(item)
        count += 1
        if print_updates and count % 100 == 0:
            print(count)

    return items


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
                                     limit=32,
                                     print_updates=True):
    """Retrieve all comments from the given submission."""

    submission.replace_more_comments(limit=limit, threshold=1)

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
    submissions = unroll_generator(submissions_gen,
                                   print_updates=print_updates)

    return submissions


def get_comments_from_redditor(redditor_name,
                               limit=1000,
                               reddit_obj=None,
                               print_updates=True):
    """Retrieve the most recent comments from the given redditor."""

    if reddit_obj is None:
        reddit_obj = praw.Reddit(USER_AGENT)

    redditor = reddit_obj.get_redditor(redditor_name)

    comments_gen = redditor.get_comments(limit=limit)
    comments = unroll_generator(comments_gen, print_updates=print_updates)

    return comments
