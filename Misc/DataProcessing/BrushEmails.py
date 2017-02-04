import re
import EnronDB

def regexp_pos(s, pattern):
    '''Returns -1 if pattern was not found, otherwise it returns the position of the regex'''
    search_res = re.search(pattern, s)
    if search_res is None:
        return -1
    return search_res.start()

def remove_block(s, start_pattern, end_patterns):
    lines = s.split('\n')
    filtered_lines = []
    filtering = False
    for line in lines:
        if regexp_pos(line.lower(), start_pattern) != -1:
            filtering = True
            continue
        for pattern in end_patterns:
            if regexp_pos(line.lower(), pattern) != -1:
                filtering = False
                filtered_lines.append('')
                continue
        if not filtering:
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)

def replace_weblinks(msg):
    #url_regex = r'[<]?http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@\.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+[>]?'
    url_regex = r'[<]?http[s]?://(?:[a-zA-Z]|[0-9]|[_.\-/@&+=$?]|[!\*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+[>]?'
    # replace the weblinks with WEBLINK token
    urls = re.findall(url_regex, msg)
    for url in urls:
        msg = msg.replace(url, 'WEBLINK')
    return msg

def remove_original_message(msg):
    return remove_block(msg, r'[- ]{3,}original message', [r'to:.*', r'cc:.*', r'subject:.*'])

def remove_forward_header(msg):
    return remove_block(msg, r'[- ]{3,}forward', [r'to:.*', r'cc:.*', r'subject:.*'])

def remove_reply_header(msg):
    return remove_block(msg, r'\w+ <?\w+@[A-Z]+>?', [r'to:.*', r'cc:.*', r'subject:.*'])

def remove_attachments(msg):
    lines = msg.split('\n')
    filtered_lines = []
    for line in lines:
        if regexp_pos(line.lower(), r'<{1,}[\w -_\':]+.[\w ]+>{1,}') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'- [\w -_\':]+.\w{2,5}$') != -1:
            filtered_lines.append('')
            continue        
        
        filtered_lines.append(line)
    return '\n'.join(filtered_lines)

def remove_confidentiality_notice(msg):
    lines = msg.split('\n')
    filtered_lines = []
    filtering = False
    for line in lines:
        if regexp_pos(line.lower(), r'confidentiality not') != -1:
            filtering = True
            continue
        if len(line) < 1:
            filtering = False
            filtered_lines.append('')
            continue
        if not filtering:
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)

def remove_misc(msg):
    lines = msg.split('\n')
    filtered_lines = []
    for line in lines:
        # Email like
        if regexp_pos(line.lower(), r'[\w/]+@\w+') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'to:\w*') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'cc:\w*') != -1:
            filtered_lines.append('')
            continue        
        if regexp_pos(line.lower(), r'from:\w*') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'phone:\w*') != -1:
            filtered_lines.append('')    
            continue
        if regexp_pos(line.lower(), r'subject:\w*') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'sent:\w*') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'sent by:\w*') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'importance:\w*') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'tel[:.]?\w*') != -1:
            filtered_lines.append('')
            continue        
        if regexp_pos(line.lower(), r'fax:?\w*') != -1:
            filtered_lines.append('')
            continue
        if regexp_pos(line.lower(), r'facsimile:\w*') != -1:
            filtered_lines.append('')        
            continue
        if regexp_pos(line.lower(), r'\d\d/\d\d/\d\d\d\d[ \t]+\d\d:\d\d( [AP]M)?') != -1:
            filtered_lines.append('')        
            continue
        
        filtered_lines.append(line)
        
    return '\n'.join(filtered_lines)

def concat_paragraph_lines(msg):
    lines = msg.split('\n')
    
    cat_lines = []
    tmp_line = lines[0] + ' '
    i = 1
    while i < len(lines):
        if len(lines[i].strip()) < 1:
            cat_lines.append(tmp_line)
            tmp_line = ''
        else:
            tmp_line += lines[i] + ' '
        i += 1
    if len(tmp_line) > 0:
        cat_lines.append(tmp_line)
    
    return '\n'.join(cat_lines)

def get_email_from_db(email_id):
    '''Gets a list of the email body from the database'''
    edb = EnronDB.EnronDB()
    edb.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo','enron_experiment')
    body_list = edb.get_body(email_id)
    return body_list

def get_emails_from_db():
    '''Gets a list of the email body from the database'''
    edb = EnronDB.EnronDB()
    edb.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo','enron_experiment')
    body_list = edb.get_all_bodies_with_id()
    return body_list

def update_email(email_id, body):
    edb = EnronDB.EnronDB()
    edb.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo','enron_experiment')
    edb.update_brushed_body(email_id, body)
    
def update_lines(email_id, body_lines):
    edb = EnronDB.EnronDB()
    edb.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo','enron_experiment')
    edb.update_brushed_lines(email_id, body_lines)
    
def process_email(msg):
    lines = msg.split('\n')
    stripped_lines = []
    for line in lines:
        # Remove the empty spaces, tabs and > of forwarded or replied messages
        strpd_line = line.lstrip(' >\t')
        # Replace lines that only contain '?' with empty space
        if strpd_line == '?':
            strpd_line = ''
        stripped_lines.append(strpd_line)
    brushed_body = '\n'.join(stripped_lines)

    # REPLACE weblinks
    brushed_body = replace_weblinks(brushed_body)

    # REMOVE the forwarding/replying blocks
    # ORIGINAL MESSAGE
    filt_1_body = remove_original_message(brushed_body)
    # FORWARDED BY
    filt_2_body = remove_forward_header(filt_1_body)
    # REPLY no separating line header
    filt_3_body = remove_reply_header(filt_2_body)
    # ATTACHMENT placeholders i.e. <file_name>
    filt_4_body = remove_attachments(filt_3_body)
    # CONFIDENTIALITY NOTICE paragraphs from the company
    filt_5_body = remove_confidentiality_notice(filt_4_body)
    # EXTRAS any other eleemnt that could not be removed 
    # TODO: improve this through analysis
    final_body = remove_misc(filt_5_body)

    # Replace more than two new lines into two newlines
    if re.search('\n{3,}', final_body, re.IGNORECASE):
        r = re.compile(r'\n{3,}', re.IGNORECASE)
        final_body = r.sub(r'\n\n', final_body) # substitute string        

    # remove the empty spaces at the beginning and the end
    strip_body = final_body.strip()

    #cat_body = concat_paragraph_lines(strip_body)
    return strip_body

def brush_emails():
    # Get all the bodies from the emails and their respective id's
    emails = get_emails_from_db()
    
    # For each of the emails
    for email_id, email_body in emails:
        print 'PARSING EMAIL: %d'%(email_id)

        # Process the email body
        processed_body = process_email(email_body)
        
        # Update the value into the brushed table
        update_email(email_id, processed_body)
        
        cat_lines = concat_paragraph_lines(processed_body)
        update_lines(email_id, cat_lines)

def test():
    test_id = 948
    test_mail = get_email_from_db(test_id)
    processed_body = process_email(test_mail)
    update_email(test_id, processed_body)
    
if __name__=='__main__':
    brush_emails()
    