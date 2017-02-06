'''
Author: Salvador Medina
This script samples emails from the 10-class dataset found in
writes them into disk and stores them in a zip file
'''
import MySQLdb
import yaml
import random
import pprint
from zipfile import ZipFile
from collections import Counter

config_filename = "dbconfig.yaml"
train_filename = "enron_train.txt"
test_filename = "enron_test.txt"
test_content_filename = "enron_test_content.txt"
test_label_filename = "enron_test_label.txt"
zip_filename = "enron_ft_data.zip"

config = yaml.load(open(config_filename))

db = MySQLdb.connect(host=config['host'],
                     user=config['user'],
                     passwd=config['passwd'],
                     db=config['db'])

cursor = db.cursor()
cursor.execute('''SELECT label, body FROM enron_labeled''')

query_res = cursor.fetchall()

data = []
for label,body in query_res:
    data.append((label, body.strip()))

random.seed(21345)
random.shuffle(data)

train_data_size = int(len(data)*0.7)
train_data = data[:train_data_size]
test_data = data[train_data_size:]

print 'Total samples:\t%d'%(len(data))
print 'Train samples:\t%d'%(len(train_data))
print 'Test samples:\t%d'%(len(test_data))

# STORE train data
with open(train_filename, 'w') as write_file:
    for label, body in train_data:
        formatted_entry = '''__label__%s %s\n''' % (label, ' '.join(body.splitlines()))
        write_file.write(formatted_entry)

with open(test_filename, 'w') as test_file:
    with open(test_content_filename, 'w') as content_file:
        with open(test_label_filename, 'w') as label_file:
            for label, body in test_data:
                # complete test write
                clean_body = ' '.join(body.splitlines())
                test_entry = '''__label__%s %s'''%(label, clean_body)
                test_file.write('''%s\n'''%(test_entry))
                # only the labels in order
                label_file.write('%s\n' % (label))
                # only the content same order as labels
                formatted_entry = '''%s\n''' % (clean_body)
                content_file.write(formatted_entry)

#zip all the files into one
with ZipFile(zip_filename, 'w') as zip_file:
    zip_file.write(train_filename)
    zip_file.write(test_filename)
    zip_file.write(test_label_filename)
    zip_file.write(test_content_filename)

## Print distribution
pp = pprint.PrettyPrinter(indent=4)
train_labels = map(lambda x: x[0], train_data)
c = dict(Counter(train_labels))
pp.pprint( c )
test_labels = map(lambda x: x[0], test_data)
c = dict(Counter(test_labels))
pp.pprint( c )