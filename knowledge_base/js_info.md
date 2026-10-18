## How JS hadles JSON:
1) JSON.stringify(obj): converts object->JSON-text
  Example:
    const note = { id: 1, text: 'Buy milk', done: false, tag: null };
    console.log(note);
    const json = JSON.stringify(note);
    console.log(json);
    console.log(typeof json);

  Result:
    object
    {"id":1,"text":"Buy milk","done":false,"tag":null}
    string

2) response.json() or JSON.parse(text): converts JSON-text->Object
  Example:
    const note = { id: 1, text: 'Buy milk', done: false, tag: null };
    console.log(typeof note);
    const json = JSON.stringify(note);
    console.log(json);
    console.log(typeof json);

    const back = JSON.parse(json);

    console.log(back);
    console.log(typeof back);
    console.log(back.text);

  Result:
    object
    {"id":1,"text":"Buy milk","done":false,"tag":null}
    string

    {id: 1, text: 'Buy milk', done: false, tag: null}
      done: false
      id: 1
      tag: null
      text: "Buy milk"

    object
    Buy milk


## Requests in JS
  const response = await fetch('/api/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'from console' }),
  });
  # syntax:
  fetch([address], [settings]); - without settings, 'fetch' does only GET requests
  Why JSON.stringify? - because body should always be a text
  
  console.log(response.status);
  console.log(await response.json());

  Result:
    201
    {id: 7, text: 'from console', created_at: '2026-10-18 11:15:02.123456'}


