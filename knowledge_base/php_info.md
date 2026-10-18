PHP-FPM= FastCGI Process Manager - it's a way to start PHP as continuous working service, which accepts connections and execs PHP-scripts

Process Manager = keeps poll of workers (working PHP processes). When request received, free worker takes it and executes script. FPM itself handles creation, restart and deleting workers.

PHP-FPM doesn't understand HTTP, it speaks exclusively on FastCGI. Browser(client) sends HTTP requests. That's where Nginx needed:

Nignx between Client and PHP does:
1) Receives HTTP requests from Client
2) Returns static files itself
3) Requests to PHP converts to FastCGI and passes to php:9000
4) Response from PHP_FPM returns to Client as HTTP


Arrays in PHP:
  $list = ['apple', 'pear'];
  $assoc = ['id' => 1, 'text' => 'Buy milk'];
  $mixed = [0 => 'a', 'name' => 'b'];

  echo 'list:  ' . gettype($list) . "\n";
  echo 'assoc: ' . gettype($assoc) . "\n";
  echo 'mixed: ' . gettype($mixed) . "\n";

  Result:
  list:  array
  assoc: array
  mixed: array

  var_dump(array_keys($list));
  var_dump(array_keys($assoc));
  var_dump(array_is_list($list));
  var_dump(array_is_list($assoc));

  Result:
  array(2) { [0]=> int(0)  [1]=> int(1) }
  array(2) { [0]=> string(2) "id"  [1]=> string(4) "text" }
  bool(true)
  bool(false)

How PHP handles JSON:
  1) json_encode($notes): converts array->JSON-text
    $note = ['id' => 1, 'text' => 'Buy milk', 'done' => false, 'tag' => null];

    $json = json_encode($note);

    echo "\$note is: " . gettype($note) . "\n";
    echo "After json_encode: " . $json . "\n";
    echo "\$json is: " . gettype($json) . "\n";

    Result:
    $note is: array
    After json_encode: {"id":1,"text":"Buy milk","done":false,"tag":null}
    $json is: string


  2) json_decode($raw, true): converts JSON-text->array
    # syntax:
    $note = associative array
    json_encode(); = ecncode = code
    $json = string with JSON-text
    gettype($json) = string: result is text, not data

    Example:
      $note = ['id' => 1, 'text' => 'Buy milk', 'done' => false, 'tag' => null];

      $json = json_encode($note);

      echo "\$note is: " . gettype($note) . "\n";
      echo "After json_encode: " . $json . "\n";
      echo "\$json is: " . gettype($json) . "\n";

      $back = json_decode($json, true);
      $back_no_associative_array = json_decode($json);

      var_dump($back);
      var_dump($back_no_associative_array);

    Result:
      $note is: array
      After json_encode: {"id":1,"text":"Buy milk","done":false,"tag":null}
      $json is: string
      array(4) {
        ["id"]=>
        int(1)
        ["text"]=>
        string(8) "Buy milk"
        ["done"]=>
        bool(false)
        ["tag"]=>
        NULL
      }
      object(stdClass)#1 (4) {
        ["id"]=>
        int(1)
        ["text"]=>
        string(8) "Buy milk"
        ["done"]=>
        bool(false)
        ["tag"]=>
        NULL
      }