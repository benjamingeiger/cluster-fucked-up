#!/bin/sh

rm -f reddit.db
sqlite3 reddit.db < init_reddit_database.sql

rm -f graph.db
sqlite3 graph.db < init_graph_database.sql
