# Vulnerabilities

### INSERT SQL injection

В функционале загрузки постов отсутствует санитизация пользовательских данных, ввиду чего можно было эсплуатировать `INSERT SQLi`.

```python

def _store_post(self, post_id, title, content, token=''):
    db = sqlite3.connect(self.db_path)
    c = db.cursor()

    query = '''
        INSERT INTO posts(post_id, title, content, token)
        VALUES(%s, \"%s\", \"%s\", \"%s\")
        ''' % (post_id, title, content, token)

    c.execute(query)
    db.commit()
 ```
 
 [sploit](insert_sqli.py)

### Type confusion

Внутри самого приложения приватность/публичность постов идентифицировалась знаком числового `post_id` (если `post_id < 0` - приватный, иначе публичный). При обработке запроса на получение поста, сервис не проверяет на соотвествие типы, присланных пользователем, данных внутри `JSON`, таким образом пользователь может отправить такой `JSON` в котором `post_id` был бы не числом, а строкой и таким образом обойти проверку на приватность/публичность (то есть даже при отрицательном `post_id` сервер обработает запрос как будто запрошен публичный пост) т.к. в python
`"" > 0 == True`, далее `post_id` подставляется в запрос к базе данных и обрабатывается.

```python

post_id = request.json['post_id']
if post_id > 0:
    res = storage.get_public_post(post_id)

elif post_id < 0:
    token = request.json['token']
    res = storage.get_private_post(post_id, token)
```

[sploit](type_confusion.py)
