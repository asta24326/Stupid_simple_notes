<?php

declare(strict_types=1);
// setting strict typisation

function getPdo(): PDO
{
  $host = getenv('DB_HOST');
  $port = getenv('DB_PORT');
  $name = getenv('DB_NAME');
  $user = getenv('DB_USER');
  $password = getenv('DB_PASSWORD');

  $dsn = "pgsql:host=$host;port=$port;dbname=$name";
  // syntax:
  // dsn= Data Source Name, line says to PDO where to connect

  return new PDO($dsn, $user, $password, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,
    // syntax:
    // ATTR_ERRMODE - exceptions mode, so we could catch errors. Options are: ERRMODE_SILENT and ERRMODE_WARNING.
    // ATTR_DEFAULT_FETCH_MODE - to convert lines from db from associative array to normal array
    // ATTR_EMULATE_PREPARES = prepared statement=2-step exchanging with DB
  ]);
}