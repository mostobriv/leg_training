# Vulnerabilities

### Weak token generation

В функционале генерации токенов используется слабая функция для получения нового токена.

```python
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
 ```
 
 [sploit](exploit.py)
 
 ### Admin password in SQL database
 
 В созданной базе данных заведен пользователь с ником admin, который получает доступ к просмотру всех секретов
