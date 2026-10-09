<?php

declare(strict_types=1);

// Reading settings from environment variables
$host = getenv('DB_HOST');
$port = getenv('DB_PORT');
$name = getenv('DB_NAME');
$user = getenv('DB_USER');
$password = getenv('DB_PASSWORD');
/* syntax:
 $[name] = variable in php, types are not declared
*/


$dsn = "pgsql:host=$host;port=$port;dbname=$name";
/* syntax:
DSN = Data Source Name - string which says to PDO where and to which drivers to connect
pgsql = prefix that choosing drver (pdo_pgsq; in our case)
host=..=pairs key=value
*/

try {
  $pdo = new PDO($dsn, $user, $password, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
  ]);
  /* syntax:
  ATTR_ERRMODE= attribute error mode 
  ERRMODE_EXCEPTION = in case of error, throw exception. By default PDO stays silent and gives warning, so we can miss and error. Exception prevents it

  ATTR_DEFAULT_FETCH_MODE = fetch associative - give data as associative array, like key=value, without extra indexing with numbers(like by defaukt)
  */

  $version = $pdo->query('SELECT version()')->fetchColumn();
  /* syntax:
  fetchColumn() = to take one value of the first column
  fetchAll() = to get all rows as array of arrays
  */
  
  echo "Postgres: $version\n";
  $database = $pdo->query('SELECT current_database()')->fetchColumn();
  echo "Connected to database: $database\n";
  /*  syntax:
  current_database() = SQL fucntion of Postgres, that returns db name ti which we're connected. There is no need for tables. Output will show notes_app, and we will see that connection is right. 
  fetchColumn()
  */
} catch (PDOException $e) {
  fwrite(STDERR, "DB error: " . $e->getMessage() . "\n"); 
  /* syntax:
   fwrite = file to write
  */
  exit(1);
}


