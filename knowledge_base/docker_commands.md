## Start containers in the background
docker compose up -d
# syntax:
compose=start all together
-d = detach, start in the background

# start containers with wait for healthy status
docker compose up -d -- wait
# syntax:
--wait = don't return control until all services are healthy

# command to check health through github ci
docker compose exec -Y db psql -U app -d notes -tAc "SELECT 1"
# syntax:
-T = turn-off TTY(pseudoterminal), cuz in CI there is no terminal and exec can fail without -T
-tAc "SELECT 1" = 
	-t = tuples only, only data without headers
	-A = unaligned by columns
	-c = command
	SELECT 1 = db query, that should return 1 if all good
	After that CI check command return code, if 0 = healthy

# Check containers status
gocker compose ps
# syntax:
ps=process status

# Look logs services
docker compose logs [service_name]
docker compose logs [service_name] -f 
# syntax:
-f=follow in realtime

# Enter container
docker compose exec db bash
docker compose exec db psql _U admin -d
# syntax:
bash = open terminal inside container
psql = PostgreSQL interactive terminal
-U admin = user flag
-d notes = [database] with name [notes]

# Stop containers
docker compose down
docket compose down -v
# syntax:
-v = flag "volumes" - clears all volumes

# start backend php container
docker build -t notes-php-test ./backend
# syntax:
docker build = build image according to Dockerfile
-t notes-php-test = --tag = give image a name/tag [notes-php-test]
./backend = build context, folder where Dockerfile is

# remove unused container
docker rmi notes-php-test
# syntax:
rmi = remove image

# to be continued...