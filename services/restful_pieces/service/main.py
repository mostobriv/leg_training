import sqlite3
from flask import Flask, request, jsonify

DB_PATH = './posts.db'
PORT    = 17649


app = Flask(__name__)
storage = None

class Storage:
    def __init__(self, db_path):
        self.db_path = db_path
        self.priv_edge, self.pub_edge = self._get_posts_edges()

    def _get_posts_edges(self):
        db = sqlite3.connect(self.db_path)
        c = db.cursor()

        query = '''
            SELECT value FROM posts_total
            WHERE type = "private" OR type = "public"
            '''

        c.execute(query)
        try:
            priv = int(c.fetchone()[0])
            pub = int(c.fetchone()[0])

        except:
            query = '''
                INSERT INTO posts_total(type, value)
                VALUES(?, ?)
                '''
            priv, pub = 1, 1
            c.execute(query, ('private', priv))
            db.commit()

            c.execute(query, ('public', pub))
            db.commit()

        return priv, pub

    def _inc_posts_edge(self, edge_id):
        assert edge_id in ['private', 'public']

        db = sqlite3.connect(self.db_path)
        c = db.cursor()

        query = '''
            UPDATE posts_total
            SET value = ? WHERE type = ?
            '''

        if edge_id == 'private':
            self.priv_edge+= 1
            new_val = self.priv_edge
        else:
            self.pub_edge+= 1
            new_val = self.pub_edge

        c.execute(query, (new_val, edge_id))
        db.commit()

    def get_private_post(self, post_id, token):
        db = sqlite3.connect(self.db_path)
        c = db.cursor()

        query = '''
            SELECT token FROM posts
            WHERE post_id = ?
            '''
        c.execute(query, [post_id])
        stoken = c.fetchone()[0]
        if stoken != token:
            return None

        return self._get_post(post_id)

    def get_public_post(self, post_id):
        return self._get_post(post_id)

    def _get_post(self, post_id):
        db = sqlite3.connect(self.db_path)
        c = db.cursor()

        query = '''
            SELECT title, content FROM posts
            WHERE post_id = ?
            '''

        c.execute(query, [post_id])
        post = c.fetchone()
        if post is None:
            return None

        return {'title': post[0], 'content': post[1]}

    def store_public_post(self, title, content):
        self._store_post(self.pub_edge, title, content)
        self._inc_posts_edge('public')

        return self.pub_edge - 1
        
    def store_private_post(self, title, content, token):
        self._store_post(-self.priv_edge, title, content, token)
        self._inc_posts_edge('private')

        return -(self.priv_edge - 1)

    def _store_post(self, post_id, title, content, token=''):
        db = sqlite3.connect(self.db_path)
        c = db.cursor()

        query = '''
            INSERT INTO posts(post_id, title, content, token)
            VALUES(%s, \"%s\", \"%s\", \"%s\")
            ''' % (post_id, title, content, token)

        c.execute(query)
        db.commit()


@app.route('/get', methods=['GET'])
def get_post():
    global storage
    result_json = dict()

    if request.is_json:
        print request.json
        try:
            post_id = request.json['post_id']
            if post_id > 0:
                res = storage.get_public_post(post_id)

            elif post_id < 0:
                token = request.json['token']
                res = storage.get_private_post(post_id, token)

            else:
                result_json['status']   = 'error'
                result_json['data']     = 'Are you dumb or wut?'
                return result_json

            if res is None:
                result_json['status']   = 'error'
                result_json['data']     = 'No posts with such post_id or your token is incorrect'
            else:
                result_json['status']   = 'success'
                result_json['data']     = res

        except KeyError:
            result_json['status']   = 'error'
            result_json['data']     = 'Missing fields in JSON'

        except Exception as e:
            raise e
            result_json['status'] = 'error'
            result_json['data']   = 'An error occured on server side'

    else:
        result_json['status']   = 'error'
        result_json['data']     = 'Request isn\'t in JSON format'

    print result_json
    return jsonify(result_json)


@app.route('/store', methods = ['POST'])
def store_post():
    global storage
    result_json = dict()

    if request.is_json:
        try:
            title   = request.json['title']
            content = request.json['content']
            public  = request.json['public']

            if public:
                post_id = storage.store_public_post(title, content)
                
            else:
                token = request.json['token']
                post_id = storage.store_private_post(title, content, token)

            result_json['status'] = 'success'
            result_json['data']   = {'post_id': post_id}

        except KeyError as e:
            result_json['status']   = 'error'
            result_json['data']     = 'Missing fields in JSON'

        except Exception as e:
            raise e
            result_json['status'] = 'error'
            result_json['data']   = 'An error occured on server side'

    else:
        result_json['status']   = 'error'
        result_json['data']     = 'Request isn\'t in JSON format'

    print result_json
    return jsonify(result_json)


if __name__ == '__main__':
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    cmd = '''
        CREATE TABLE IF NOT EXISTS
            posts(
                pid INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                title TEXT,
                content TEXT,
                token TEXT
            )'''
    c.execute(cmd)
    db.commit()

    cmd = '''
        CREATE TABLE IF NOT EXISTS
            posts_total(
                pid INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                value INTEGER
            )'''

    c.execute(cmd)
    db.commit()

    global storage
    storage = Storage(DB_PATH)

    app.run(host='0.0.0.0', port=PORT, debug=True)