#!/usr/bin/python
import MySQLdb
import random
import os

save_dir = '/Users/zal/CMU/InMind/Devel/EmailUnderstanding/data/SchedulingSample'

db = MySQLdb.connect(host="holbox.lti.cs.cmu.edu",  # your host, usually localhost
                     user="inmind",                 # your username
                     passwd="yahoo",                # your password
                     db="enron_experiment")         # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# Use all the SQL you like
cur.execute("SELECT id,raw_body FROM email_prediction WHERE probability>.95")

# print all the first cell of all the rows
scheduling_emails = []
for row in cur.fetchall():
    scheduling_emails.append((row[0], row[1]))

random.seed(3141592)
random_idx = random.sample(range(0, len(scheduling_emails)), 200)
indices = []
for rid in random_idx:
    cur_email = scheduling_emails[rid]
    indices.append(cur_email[0])
    with open(os.path.join(save_dir, '%d.txt'%cur_email[0]), 'w') as save_file:
        save_file.write(cur_email[1])
        save_file.close()


index_file = open(os.path.join(save_dir, 'index.csv'), 'w')
indices.sort()
for idx in indices:
    index_file.write("%d\n"%idx)
index_file.close()

db.close()