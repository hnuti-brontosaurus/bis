# BIS backend + administration

`git clone`

`.env` do `./`

`db.json` do `./backend/old_database_dump/`

`make` - build docker images

`make backend` - run backend

`docker exec -it bis-backend sh` + `python manage.py reset` - import old db

```bash
# Testing uses plugin for local storage
npm i --save-dev cypress-localstorage-commands
make open_cypress  # open cypress
```

`/admin/code_login/` - login without frontend

`python manage.py shell` - open django shell

```python
from bis.models import User
token = f"Token {User.objects.get(email='asdf').auth_token.key}"
```

`git remote add dev root@dev.bis.lomic.cz:/home/git/repo.git`

`git push -f dev master`

`PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USERNAME -h $DB_HOST -d $DB_NAME -F t -f /app/media/mydb.dump`

```bash
docker stop bis-backend
PGPASSWORD=123 dropdb -U postgres -h localhost postgres
PGPASSWORD=123 createdb -U postgres -h localhost postgres
PGPASSWORD=123 pg_restore -U postgres -h localhost -d postgres --no-owner -F t /home/lamanchy/laman/Downloads/mydb.dump
```
