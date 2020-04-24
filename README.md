# legs_training
@yalegko's A/D training prepared by `pid||kill` team w/ help of [@elmikuliofondesashkin](https://github.com/mikulinsky)

## Services
| Service | Language | Checker | Sploits | Authors |
|---------|----------|---------|---------|---------|
| **[keepnotes](services/keepnotes/)** | python3 | [checker](checkers/keepnotes/) | [sploits](sploits/keepnotes) | [@lizatrif](https://github.com/lizatrif) & [@katrinhey](https://github.com/Katrinehey) |
| **[code-snippets](services/code_snippets/)** | python3 (Flask) | [checker](checkers/code-snippets/) | [sploits](sploits/code-snippets) | [@dxbluff](https://github.com/dxbluff) & [@kranonetka](https://github.com/kranonetka) |
| **[restful_pieces](services/restful_pieces/)** | python2 (Flask) | [checker](checkers/restful_pieces/) | [sploits](sploits/restful_pieces/) | [@mostobriv](https://github.com/mostobriv) |


## Descriptions

### keepnotes

Консольный сервис хранения заметок, довольно простой функционал: регистрация пользователя, авторизация, положить заметку, забрать заметку по токену

### code-snippets

Копия [pastebin.com](https://pastebin.com) на минималках. Можно загрузить свой снипет, он может быть публичным и приватным, доступ к приватным снипетом ограничивается необходимостью наличия прямой ссылки на него, так же есть возможность поиска снипета по подстроке.

### restful_pieces

`REST api` приложение, логика довольно простая: загрузить пост, по `post_id` прочитать что загрузилось, посты могут быть приватными или публичными, доступ к приватным ограничен необходимостью знания секретного токена предоставляемого автором приватного поста.
