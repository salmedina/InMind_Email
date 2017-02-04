import re
import string
import EnronDB

def remove_invalid_unicode(inStr):
    return re.sub(r'[^\x00-\x7f]',r' ',inStr)

def get_emails_from_db(edb):
    '''Gets a list of the email body from the database'''
    body_list = edb.get_all_brushed_lines_with_id()
    return body_list

def store_one_liner(edb, email_id, text):
    edb.update_brushed_one_line(email_id, text)

def main():
    '''Convert to one liners the brushed documents'''
    # Initialize the DB
    edb = EnronDB.EnronDB()
    edb.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo','enron_experiment')
    
    # Read all the bodies from the brushed table
    emails = get_emails_from_db(edb)
    
    exclude_set = set(string.punctuation)
    
    # For each of the emails 
    for email_id, body in emails:
        print 'Processing email %d '%(email_id)
        # To lower case and remove unwanted chars 
        body = ''.join(ch for ch in body.lower().translate(None, '\n\t\r') if ch not in exclude_set)
        # Store in DB
        store_one_liner(edb, email_id, body)

if __name__=='__main__':
    main()