'''
Created on Jul 21, 2016

@author: zhongzhu
'''
import os
import re

import DBUtil


db = DBUtil.initDB()

for filename in os.listdir("../data/AllEmails/NonschedulingEmails"): 
    if filename == '.DS_Store':
        continue
    email_id = int(filename[:-10])
    db.update_brushed_email_is_scheduling(email_id, 0)

for filename in os.listdir("../data/AllEmails/SchedulingEmails"): 
    if filename == '.DS_Store':
        continue
    email_id = int(filename[:-10])
    db.update_brushed_email_is_scheduling(email_id, 1)