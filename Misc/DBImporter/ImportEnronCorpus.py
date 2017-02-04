#!/usr/bin/env python

import sys
import os
import email
import MySQLdb
import ConfigParser
import collections
from email.Iterators import typed_subpart_iterator

'''This tuple stores the configuration for DB creation'''
DBConfig = collections.namedtuple('DBConfig', 'server user password name')

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

def insert_email_db(db, msg):
    '''Inserts e-mail into the database where msg is a message object resulting from email package'''
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
    '''Verifies if the email with msg_id exists in the database'''
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

def import_corpus(corpus_path, db_config):
    '''Imports the corpus files into the Database, the messages are parsed using email which takes care of MIME'''
    db = build_db(db_config)
    if db is None:
        print 'ERROR: ImportEnronCorpus::import_corpus could not build db object'
        sys.exit(-1)

    error_list = []
    for user_name in os.listdir(corpus_path):
        if user_name == '.DS_Store':
            continue
        user_email_dir = os.path.join(corpus_path, user_name, 'all_documents')
        print 'Insert e-mails of user: %s'%(user_name)
        if os.path.isdir(user_email_dir):
            for email_file in os.listdir(user_email_dir):
                cur_email = email.message_from_file(open(os.path.join(user_email_dir, email_file)))
                if not exists_email_db(db, cur_email['Message-ID']):
                    success,err_msg = insert_email_db(db, cur_email)
                    if not success:
                        error_list.append( (os.path.join(user_name,'all_documents',email_file), err_msg) )
        else:
            print '{} does not have all_documents dir'.format(user_name)

    with open('insert_error.log', 'wb') as err_file:
        for email_path, error_msg in error_list:
            err_file.write('{}\t{}'.format(email_path, error_msg))
        err_file.close()

def build_db(db_config):
    '''Builds a MySQLdb instance based on the dbconfi named tuple'''
    if type(db_config) != DBConfig:
        print 'ERROR: wrong db config type %s'%(type(DBConfig))
        sys.exit(-1)

    try:
        db = MySQLdb.connect(host=db_config.server,
                               user=db_config.user,
                               passwd=db_config.password,
                               db=db_config.name)
    except Exception, e:
        print 'ERROR: while connecting to database'
        print e.message
        return None

    return db

def load_database_config(config_file):
    '''Loads the configuration file and returns data in a named tuple'''
    configParser = ConfigParser.ConfigParser()
    configParser.read(config_file)
    db_config = DBConfig(configParser.get('Database', 'server'),
                         configParser.get('Database', 'user'),
                         configParser.get('Database', 'password'),
                         configParser.get('Database', 'name'))
    return db_config

if __name__=='__main__':
    if len(sys.argv) < 3:
        print 'Usage: python ImportEnronCorpus.py <enron_root_path> <database_config>'

    enron_corpus_path = sys.argv[1]
    db_config_path = sys.argv[2]
    # Load config file
    db_config = load_database_config(db_config_path)
    # Import corpus into database
    import_corpus(enron_corpus_path, db_config)
