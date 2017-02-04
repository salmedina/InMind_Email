#!/usr/bin/env python
import sys
import os
import email
import solr
import MySQLdb
from email.Iterators import typed_subpart_iterator

def get_body(message):
    """Get the body of the email message"""
    if message.is_multipart():
        #get the plain text version only
        text_parts = [part
                      for part in typed_subpart_iterator(message, 'text', 'plain')]
        body = []
        for part in text_parts:
            charset = get_charset(part, get_charset(message))
            body.append(part.get_payload(decode=True))

        return "\n".join(body).strip()
    else:
        body = message.get_payload(decode=True)
        return body.strip()

def build_db():
    try:
        db = MySQLdb.connect(host='holbox.lti.cs.cmu.edu',
                               user='inmind',
                               passwd='yahoo',
                               db='enron_experiment')
    except Exception, e:
        print 'ERROR: while connecting to database'
        print e.message
        return None

    return db

def insert_email_solr(db, msg):
    esc = db.escape_string
    msg_body = esc(get_body(msg))
    cursor = db.cursor()
    try:
        ins_query = '''INSERT INTO enron_corpus (message_id, date, mime_type, from_addr, to_addr, subject, body, path, username) \
                        VALUES('{msg_id}','{date}','{mime_type}','{from_addr}','{to_addr}','{subject}','{body}','{path}','{username}')'''.format(\
                        msg_id=esc(msg['Message-ID']), date=esc(msg['Date']), mime_type=esc(msg['Content-Type']), from_addr=esc(msg['From']), to_addr=esc(msg['To']),\
                        subject=esc(msg['Subject']), body=msg_body, path=esc(msg['X-Folder']), username=esc(msg['X-Origin']))
        cursor.execute(ins_query)
        db.commit()
    except Exception, e:
        db.rollback()
        return False,e.message

    return True,''

def exists_email_db(db, msg_id):
    msg_id = db.escape_string(msg_id)
    cursor = db.cursor()
    try:
        count_query ='''SELECT COUNT(*) FROM enron_corpus WHERE message_id="{}"'''.format(msg_id)
        cursor.execute(count_query)
        (num_rows,) = cursor.fetchone()
    except Exception, e:
        print 'ERROR: while looking for existing email ::', e.message
        return False

    return num_rows > 0

def insert_email_solr(core, msg, subdir):
    msg_body = get_body(msg)
    try:
        core.add(message_id=msg['Message-ID'], date=msg['Date'], mime_type=msg['Content-Type'], from_addr=msg['From'], to_addr=msg['To'],\
                subject=msg['Subject'], body=msg_body, path=msg['X-Folder'], username=msg['X-Origin'], file=subdir)
        core.commit()
    except Exception, e:
        return False, e.message

    return True, ''


def main(enron_path, solr_url):
    if not os.path.isdir(enron_path):
        print 'ERROR: The given path is not a dir'
        return

    try:
        solr_core = solr.SolrConnection(solr_url)
    except Exception, e:
        print 'ERROR: could not connect to core.',e.message
        return

    error_list = [] #Import error (file_path, error_message)
    for path, subdirs, files in os.walk(enron_path):
        print '({}) - {}'.format(len(files), path)
        for filename in files:
            if filename == '.DS_Store':
                continue #Simply ignore it
            tmp_email_path = os.path.join(path, filename)
            subpath = tmp_email_path.replace(enron_path, '')
            cur_email = email.message_from_file( open(tmp_email_path) )
            success, err_msg = insert_email_solr(solr_core, cur_email, subpath)
            if not success:
                error_list.append((tmp_email_path, err_msg))

    with open('insert_error_solr.log', 'wb') as err_file:
        for email_path, error_msg in error_list:
            err_file.write('{}\t{}'.format(email_path, error_msg))
        err_file.close()


if __name__=='__main__':
    enron_path = sys.argv[1]
    solr_url = sys.argv[2]

    main(enron_path, solr_url)
