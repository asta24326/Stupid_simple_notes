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

  $notes = $pdo->query('SELECT * FROM notes')->fetchAll();
  echo "Notes (" . count($notes) . "):\n";
  echo json_encode($notes, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), "\n";
  /*  syntax:
  json_encode = convert array to JSON-text
  JSON_PRETTY_PRINT = beatifully with indents and tabs
  JSON_UNESCAPED_UNICODE = not to convert to cyrillik to \u0431-sequence 
  */
} catch (PDOException $e) {
  fwrite(STDERR, "DB error: " . $e->getMessage() . "\n"); 
  /* syntax:
   fwrite = file to write
  */
  exit(1);
}


