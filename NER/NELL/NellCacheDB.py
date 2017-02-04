import MySQLdb
import hashlib
import json

class NellCacheDB:
    def __init__(self, host, user, passwd, db_name):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db_name = db_name
        # Mini-cache
        self.last = {}
        self.last['text'] = ''
        self.last['hash_key'] = ''
        self.last['annotation'] = '{}'
        self.connect()

    def connect(self):
        self.db = MySQLdb.connect(host=self.host,
                                  user=self.user,
                                  passwd=self.passwd,
                                  db=self.db_name)
        self.cursor = self.db.cursor()

    def hash_text(self, text):
        hash_object = hashlib.sha256(text)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def in_cache(self, text):
        hkey = self.hash_text(text)
        query_str = '''SELECT COUNT(*) FROM nell_cache WHERE hash_key="%s"'''%(hkey)
        self.cursor.execute(query_str)
        query_res = self.cursor.fetchone()
        return query_res[0]>0

    def get_annotation(self, text):
        hash_key = self.hash_text(text)
        query_str = '''SELECT annotation, text_len FROM nell_cache WHERE hash_key="%s"'''%(hash_key)
        self.cursor.execute(query_str)
        res_annotation, res_len = self.cursor.fetchone()

        if res_len != len(text):
            return ''
        return json.loads(res_annotation)

    def save_annotation(self, text, annotation):
        hash_key = self.hash_text(text)
        anno_str = json.dumps(annotation)

        query_str = '''INSERT INTO nell_cache (hash_key, annotation, text_len, text) VALUES (%r, %r, %d, %r)'''%(hash_key, anno_str, len(text), text)
        self.cursor.execute(query_str)
        self.db.commit()
