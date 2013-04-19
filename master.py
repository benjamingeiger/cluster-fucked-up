from __future__ import print_function

import praw

import database

from definitions import USER_AGENT


DATABASE_NAME = "reddit.db"

SEED_SUBREDDITS = ["nsfw", "pics", "news", "worldnews", "funny"]

LIMIT=10

def main():
    reddit_obj = praw.Reddit(USER_AGENT)
    for subreddit in SEED_SUBREDDITS:
        database.process_subreddit(
                subreddit,
                DATABASE_NAME,
                limit=LIMIT,
                reddit_obj=reddit_obj)


if __name__ == "__main__":
    main()
