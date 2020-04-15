from socketserver import TCPServer, StreamRequestHandler, ThreadingMixIn
from _io import BufferedWriter, BufferedReader
import sqlite3
import hashlib
import random
from struct import pack
from threading import Lock
import sys

DB_FILE = './db_secret.db'

lock = Lock()

class MyHandler(StreamRequestHandler):
    def setup(self):
        super().setup()
        self.loginup = False
        self.isadmin = False

    def register(self):
        self.wfile.write(b'!_____REGISTER FORM_____!\n')
        self.wfile.write(b'   login:')
        login = self.rfile.readline().decode()
        login = login[:-1]
        self.wfile.write(b'password:')
        password = self.rfile.readline().decode()
        password = password[:-1]
        with lock:
            db = sqlite3.connect(DB_FILE)
            c = db.cursor()
            query = '''
                    SELECT * FROM users
                    WHERE login = ?
                    '''
            c.execute(query, [login])
            result = c.fetchone()
            if result:
                self.wfile.write(b'this login is already used')
            else:
                query = '''
                        INSERT INTO users(login, password)
                        VALUES (?,?)
                        '''
                c.execute(query, (login, password))
                db.commit()
                self.wfile.write(b'!_____SUCCESSFULLY_____!\n')
            db.close()

    def login(self):
        self.wfile.write(b'!_____LOGIN FORM_____!\n')
        self.wfile.write(b'   login:')
        login = self.rfile.readline().decode()
        login = login[:-1]
        self.wfile.write(b'password:')
        password = self.rfile.readline().decode()
        password = password[:-1]
        with lock:
            db = sqlite3.connect(DB_FILE)
            c = db.cursor()
            query = '''
                    SELECT * FROM users
                    WHERE login = ? AND password = ?
                    '''
            c.execute(query, (login, password))
            result = c.fetchone()
        if result:
            self.wfile.write(b'!_____SUCCESSFULLY_____!\n')
            self.loginup = True
            if login == 'admin':
                self.isadmin = True
        else:
            self.wfile.write(b'login again please\n')
            self.loginup = False

    def generate_token(self):
        with lock:
            db = sqlite3.connect(DB_FILE)
            c = db.cursor()
            query = '''
                    SELECT abvgd FROM abvgd
                    '''
            c.execute(query)
            avbgd = c.fetchone()[0]
            avbgd_new = ((((avbgd * 0xd34dc0d3) % 2 ** 32) + 0) % 2 ** 32 )
            query = '''
                    UPDATE abvgd
                    SET abvgd = ?
                    WHERE abvgd = ?
                    '''
            c.execute(query, (avbgd_new, avbgd))
            db.commit()
            db.close()
        return hashlib.md5(pack("I", avbgd_new)).hexdigest()

    def show_table(self):
        if self.loginup == True and self.isadmin == True:
            self.wfile.write(b'you are admin, so you can see all secrets\n')
            with lock:
                db = sqlite3.connect(DB_FILE)
                c = db.cursor()
                query = '''
                        SELECT * FROM secrets
                        '''
                c.execute(query)
                result = c.fetchall()
                db.commit()
                db.close()
            for row in result:
                self.wfile.write(row[1].encode() + b'\n')
        else:
            self.wfile.write(b'you are not admin\n')

    def give_secret(self):
        if self.loginup == True:
            self.wfile.write(b'print your secret here\n')
            data = self.rfile.readline().decode()
            data = data[:-1]
            token = self.generate_token()
            with lock:
                db = sqlite3.connect(DB_FILE)
                c = db.cursor()
                query = '''
                        INSERT INTO secrets(secret, token)
                        VALUES (?,?)
                        '''
                c.execute(query, (data, token))
                db.commit()
                db.close()
            self.wfile.write(b'your token is ' + token.encode() + b'\n')
        else:
            self.wfile.write(b'you need login first of all\n')

    def take_secret(self):
        if self.loginup == True:
            self.wfile.write(b'print your token here\n')
            data = self.rfile.readline().decode()
            data = data[:-1]
            print(data)
            with lock:
                db = sqlite3.connect(DB_FILE)
                c = db.cursor()
                query = '''
                        SELECT secret FROM secrets
                        WHERE token = ?
                        '''
                c.execute(query, [data])
                result = c.fetchone()
            if result:
                secret = result[0]
                self.wfile.write(b'your secret is ' + secret.encode() + b'\n')
            else:
                self.wfile.write(b'there is no such token, sorry\n')
        else:
            self.wfile.write(b'you need login first of all\n')
		
    def handle(self):
        while True:
            self.wfile.write(b'-----------------------------------------------------------\n')
            self.wfile.write(b'| print "1" if you want register in my system             |\n')
            self.wfile.write(b'| print "2" if you want login in my system                |\n')
            self.wfile.write(b'| print "3" if you want give your secret to me            |\n')
            self.wfile.write(b'| print "4" if you want take your secret from my storages |\n')
            self.wfile.write(b'| print "5" if you want see all secrets                   |\n')
            self.wfile.write(b'| print "6" if you want exit                              |\n')
            self.wfile.write(b'-----------------------------------------------------------\n')
            data = self.rfile.readline().decode()
            #print (data)
            if data == '1\n':
                self.register()
            elif data == '2\n':
                self.login()
            elif data == '3\n':
                self.give_secret()
            elif data == '4\n':
                self.take_secret()
            elif data == '5\n':
                self.show_table()
            elif data == '6\n':
                break
            else:
                break

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    pass


if __name__ == "__main__":
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    cmd = '''
            CREATE TABLE IF NOT EXISTS
                secrets(
                    pid INTEGER PRIMARY KEY AUTOINCREMENT,
                    secret TEXT,
                    token TEXT
            )'''
    c.execute(cmd)

    cmd = '''
    	    CREATE TABLE IF NOT EXISTS
    	        users(
    	            pid INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT,
                    password TEXT
    	    )'''
    c.execute(cmd)

    cmd = '''
            CREATE TABLE IF NOT EXISTS
                abvgd(
                    abvgd INT
            )'''
    c.execute(cmd)

    query = '''
            INSERT INTO abvgd(abvgd)
                VALUES (?)
            '''
    c.execute(query, [random.getrandbits(32)])
    db.commit()
	
    with ThreadingTCPServer(("", int(sys.argv[1])), MyHandler) as server:
        server.serve_forever()