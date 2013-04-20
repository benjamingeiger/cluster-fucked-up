from __future__ import print_function

import praw

import database

from definitions import USER_AGENT


DATABASE_NAME = "reddit.db"

SEED_SUBREDDITS = ["nsfw", "pics", "news", "worldnews", "funny",
                   "photography", "askreddit"]

LIMIT = 3

MAX_SUBREDDITS = 5000


def process_seed_subreddits(reddit_obj):
    for subreddit in SEED_SUBREDDITS:
        print("Processing seed subreddit: {}".format(subreddit))
        database.process_subreddit(
                subreddit,
                DATABASE_NAME,
                limit=LIMIT,
                reddit_obj=reddit_obj)


def process_next_redditor(reddit_obj, count):
    next_redditor = database.find_next_redditor(DATABASE_NAME)
    if next_redditor is None:
        print("Couldn't find next redditor.")
        return 0
    print("Processing redditor #{}: {}".format(count + 1, next_redditor))
    database.process_redditor(
            next_redditor,
            DATABASE_NAME,
            limit=LIMIT,
            reddit_obj=reddit_obj)

    return 1


def process_next_subreddit(reddit_obj, count):
    next_subreddit = database.find_next_subreddit(DATABASE_NAME)
    if next_subreddit is None:
        print("Couldn't find next subreddit.")
        return 0
    print("Processing subreddit #{}: {}".format(count + 1, next_subreddit))
    database.process_subreddit(
            next_subreddit,
            DATABASE_NAME,
            limit=LIMIT,
            reddit_obj=reddit_obj)

    return 1

def main():
    reddit_obj = praw.Reddit(USER_AGENT)

    if not database.is_seeded(DATABASE_NAME):
        process_seed_subreddits(reddit_obj)
        database.mark_seeded(DATABASE_NAME)

    count = (database.count_subreddits_processed(DATABASE_NAME)
             - len(SEED_SUBREDDITS))
    while count < MAX_SUBREDDITS:
        successes = 0

        successes += process_next_redditor(reddit_obj, count)
        successes += process_next_subreddit(reddit_obj, count)

        if successes == 0:
            break
        count += 1


if __name__ == "__main__":
    main()
