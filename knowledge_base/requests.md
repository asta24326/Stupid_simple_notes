curl -i http://localhost/api/notes
# syntax:
-curl = Client URL = console HTTP client
-i = include headers and status

curl -i -X POST -H "Content-Type: application/json" -d '{"text":"Buy milk"}' http://localhost/api/notes
# syntax:
-X POST = set request method
-H = add Header
-d = add data to request's body


curl -s http://localhost/api/notes
# syntax:
-s = silent, without progess and headers information

# Catchers
-i = show status+headers+body
-I = head, sends request only with mehod HEAD and shows only Headers