'''
Created on Jun 9, 2016

@author: zhongzhu
'''
import email
import os
import re


def clean(body):
    new_body = ""
    lines = body.split("\n")
    for line in lines:
        cleaned_line = re.sub(r"(^.*?(From|Sent|To|Cc):.*$|=20|=09|=\s*$|^.*Original Message.*$|^\s+)", "", line)
        if line.endswith("="):
            new_body += cleaned_line
        else:
            new_body += " " + cleaned_line
    return new_body

# mail_root = "/Users/zhongzhu/Documents/code/EmailUnderstanding/data/Emails_with_label"
# 
# def clean_mails(mail_dir):
#     # Traverse through all directories recursively
#     for dirpath, _, filenames in os.walk(mail_dir):
#         for filename in filenames:
#             if filename in [".DS_Store", ".gitignore"]:
#                 continue
#             filepath = os.path.abspath(os.path.join(dirpath, filename))
#             with open(filepath) as f:
#                 raw_email = email.message_from_file(f)
#                 raw_content = raw_email.get_payload()
#                 cleaned_content = clean(raw_content)
#                 
#                 new_folder = dirpath.replace("Emails_with_label", "cleaned")
#                 if not os.path.exists(new_folder):
#                     os.makedirs(new_folder)
#                 new_path = os.path.abspath(os.path.join(new_folder, filename))
#                 print(new_path)
#                 with open(new_path, "w+") as new_file:
#                     new_file.write(cleaned_content)


# if __name__ == '__main__':
# #     with open("../temp/dirty") as f:
# #         print(clean(f.read()))
#     clean_mails(mail_root)