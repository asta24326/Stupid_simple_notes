<?php

  header('Content-Type: text/plain');
  // header() - adds HTTP-header to response.
  // '{name}:{value}' - says to browser "it's a simple text, not HTML"

  echo "Hello from PHP-FPM\n";

  echo 'Method: ' . $_SERVER['REQUEST_METHOD'] . "\n";
  echo 'URI: ' . $_SERVER['REQUEST_URI'] . "\n";
  // syntax:
  // REQUEST_METHOD = stores HTTP method (GET or POST)
  // REQUEST_URI = requests path (/api/notes)
  // URI = Uniform Resource Identifier

?>