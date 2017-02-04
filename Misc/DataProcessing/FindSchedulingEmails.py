'''
Created on Jul 10, 2016

@author: zhongzhu

July 10, Zhong:
There are 120 emails under 'logistics', out of which 65 have DATE entity (based on Stanford-NER).
After manually selecting the emails, all the 'scheduling' emails are placed under '../data/SchedulingEmails'
The 'not' sub-folder is where all the non-scheduling emails (which do have dates) are stored. 

Some initial observation: under 'logistics', if the email contains DATE together with 'conference', 'meeting', 'location', it's very likely to be a scheduling email. Some even have a well-defined format.
'''
from nltk.tag.stanford import StanfordNERTagger
from nltk.tokenize import word_tokenize

import DBUtil


st = StanfordNERTagger(model_filename='/Users/zhongzhu/Documents/code/lib/stanford-ner-2015-12-09/classifiers/english.muc.7class.distsim.crf.ser.gz', path_to_jar="/Users/zhongzhu/Documents/code/lib/stanford-ner-2015-12-09/stanford-ner-3.6.0.jar")

db = DBUtil.initDB()
emails = db.get_all_brushed_emails()

print(len(emails))

scheduling_emails = []
for email in emails:
    tags = st.tag(word_tokenize(email.body))
    date_tags = [t for t in tags if t[1] == 'DATE']
    if len(date_tags):
        print(email.id, email.path)
        scheduling_emails.append(email)
        with open("../data/AllEmails/" + str(email.id) + "_email.txt", "w+") as f:
            header = "DATES: "
            for tag in date_tags:
                header += tag[0] + " | "
            f.write(header + "\n")
            f.write(email.body)
        
print(len(scheduling_emails))