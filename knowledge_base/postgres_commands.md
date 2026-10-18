# Informational commands in postgres

# to enter into db container
docker compose exec db psql -U admin -d notes_app
# syntax:
psql = client Postgres
-U = used
-d = database name

# Describe users
\du
# syntax:
\ = command for psql
d = describe
u = user

# Describe list of dbs in postgres
\l
# syntax:
l = list

# Describe tables
\dt
# syntax:
d = describe
t = tables

# Describe specific table
\d [table_name]
# syntax:
d = describe
table_name = name of the table

# Quit psql programm
\q
# syntax:
q = quit