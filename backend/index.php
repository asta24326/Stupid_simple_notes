<?php

  declare(strict_types=1);
  ini_set('display_errors', '0');
  ini_set('log_errors', '1');
  // syntax:
  // ini_set = initialisation set
  // display_error = to display errors in std_out
  // log_errors = writes error to logs

  require __DIR__ . '/db.php';
  // syntax:
  // require = connect file and execute it
  // so require opens a file and executes it from top to bottom
  // so all functions are available in main file
  // if require failed, execution stops there
  // include - another option, but only if block is optional, otherwise we won't see an error if file isn't available


  // Error handling
  function sendError(int $status, string $message): never {
    http_response_code($status);
    echo json_encode(['error' => $message]);
    exit;
  }
  // syntax:
  // : never - function never ends normally, it always stops the script(exit) or thorws exception. Control never returns back to "main"


  $method = $_SERVER['REQUEST_METHOD'];
  $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
  //  syntax:
  //  PHP_URL_PATH - argument to get only path, and drop other information
  // parse_url('/api/notes?limit=5')) res-> {[path] => "/api/notes", [query] => "limit=5"};
  // parse_url('/api/notes?limit=5', PHP_URL_PATH) res-> "/api/notes";

  header('Content-Type: application/json; charset=utf-8');
  // syntax:
  // sends header first to client

  try {
    if ($path !== '/api/notes') {
      sendError(404, 'Not found');
    }

    // GET method path
    if ($method === 'GET') {
      $pdo = getPdo();
      $statement = $pdo->query('SELECT id, text, created_at FROM notes ORDER BY id DESC');
      $notes = $statement->fetchAll();
      // syntax:
      // $statement = PDOstatement object, that stores data from DB inside
      // fetchAll() method does extract and save data as array of arrays. 
      // Example:
      // Array
      // (
      //   [0] => Array
      //       (
      //           [id] => 1
      //           [text] => Buy milk
      //       )
      //   [1] => Array
      //       (
      //           [id] => 2
      //           [text] => Call mom
      //       )
      // );
      http_response_code(200);
      echo json_encode($notes);
      exit;
    }

    // POST method path - we expect "POST /api/notes + {"text":"Buy milk"}"
    // Plan:
    // 1) Read raw body
    // 2) Parse JSON -> if broken -> 400 {"error":"Invalid JSON"}
    // 3) Check "text" field -> if none -> 400 {"error":"empty text field"}
    // 4) INSERT (preapared data) -> DB error -> 500
    // 5) If passed success -> 201 + created note

    // Step 1 - routing 
    if ($method === 'POST') {
      $raw = file_get_contents('php://input');
      
      // Step 2 - body reading and checking if JSON isn't broken
      // reading from input stream
      try {
        $data = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
        // syntax:
        // true = return array
        // 512 = max depth
        // JSON_THROW_ON_ERROR = in case of error -> throw exception
      } catch (JsonException) {
        sendError(400, 'Invalid JSON');
      }

      // Step 3 - check data form
      if (!is_array($data) || !isset($data['text']) || !is_string($data['text'])) {
        // syntax:
        // !isset($data['text']) - if key 'text' exists and not null
        // !is_string($data['text']) - if key 'text's value is not a string
        sendError(400, 'Field [text] is required and must be a string');
      }

      // Step 4 - INSERT in DB
      $pdo = getPdo();
      $statement = $pdo->prepare(
        'INSERT INTO notes (text) VALUES (:text) RETURNING id, text, created_at'
        // syntax: 
        // VALUES (:text) = placeholder
        // RETURNING = Postgres feature - to return created line as SELECT
      );
      $statement->execute(['text' => $data['text']]);
      $note = $statement->fetch();

      // Step 5 - response and block closure
      http_response_code(201);
      echo json_encode($note);
      // syntax:
      // associative array converted to JSON object
      exit;
    }

    header('Allow: GET, POST');
    sendError(405, 'Method is not allowed');
    // syntax:
    // Allow = standard header for 405 error
    // 405 = Method Not Allowed, path exists but mehtod doesn't
  } catch (Throwable $e) {
    error_log($e::class . ': ' . $e->getMessage() . ' in ' . $e->getFile() . ':' . $e->getLine());
    sendError(500, 'Internal server error');
    // syntax:
    // Throwable = catch ANY type of exception: Exception, Error and etc
    // $e::class = class name of the error
    // getNessage(), getFile(), getLine() = to get text, file and line
    // error_log(...) = to write to logs
  }
