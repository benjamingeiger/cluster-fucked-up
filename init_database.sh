#!/bin/sh

rm -f reddit.db
sqlite3 reddit.db < init_database.sql
