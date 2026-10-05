## Start containers in the background
docker compose up -d
# syntax:
compose=start all together
-d = detach, start in the background

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

# to be