PHP-FPM= FastCGI Process Manager - it's a way to start PHP as continuous working service, which accepts connections and execs PHP-scripts

Process Manager = keeps poll of workers (working PHP processes). When request received, free worker takes it and executes script. FPM itself handles creation, restart and deleting workers.

PHP-FPM doesn't understand HTTP, it speaks exclusively on FastCGI. Browser(client) sends HTTP requests. That's where Nginx needed:

Nignx between Client and PHP does:
1) Receives HTTP requests from Client
2) Returns static files itself
3) Requests to PHP converts to FastCGI and passes to php:9000
4) Response from PHP_FPM returns to Client as HTTP