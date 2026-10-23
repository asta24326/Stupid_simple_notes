// ---------------------------------------------------------------
// References to page elements (ids come from index.html).
// We look them up once here and reuse the variables below.
// ---------------------------------------------------------------
const notesList = document.getElementById('notes-list');
const noteText = document.getElementById('note-text');
const noteDate = document.getElementById('note-date');
const saveBtn = document.getElementById('save-btn');
const newNoteBtn = document.getElementById('new-note-btn');
const errorMessage = document.getElementById('error-message');

// ---------------------------------------------------------------
// State: the only two things the app "knows".
// notes      - all notes as returned by GET /api/notes
// selectedId - id of the opened note, null means "writing a new one"
// The screen is always built from these two variables.
// ---------------------------------------------------------------
let notes = [];
let selectedId = null;

/*
 * showError
 * Puts a message under the text field (red text, see style.css).
 * Used for errors from the API ({"error": "..."}) and network failures.
 */
function showError(message) {
  errorMessage.textContent = message;
}

/*
 * clearError
 * Removes the message. Called before every new action so that an old
 * error does not stay on the screen.
 */
function clearError() {
  errorMessage.textContent = '';
}

/*
  to change Save button state
*/
function updateSaveButton() {
  const textInField = noteText.value;

  if (textInField === '') {
    saveBtn.Disabled = true;
  } else {
    saveBtn.Disabled = false;
  }
}

/*
 * parseDate
 * Turns the created_at string from the API into a JS Date.
 * Postgres returns "2026-10-17 18:02:44.048033": UTC time without a
 * zone. We cut the microseconds, replace the space with "T" (ISO
 * format) and add "Z" ("this is UTC"). Without "Z" the browser would
 * treat the time as local and shift it by the timezone offset.
 */
function parseDate(createdAt) {
  return new Date(createdAt.slice(0, 19).replace(' ', 'T') + 'Z');
}

/*
 * getTitle
 * The API has no "title" field, so the title is the first line of the
 * text (like in Apple Notes). If that line is empty, show "New note".
 */
function getTitle(text) {
  return text.split('\n')[0].trim() || 'New note';
}

/*
 * renderList
 * Draws the left column from the state. It does not ask the server
 * and does not decide anything: it clears the list and builds one <li>
 * per note. The note whose id equals selectedId gets the "selected"
 * class (yellow background). Safe to call as many times as needed.
 * textContent is used (not innerHTML) so note text is never treated
 * as HTML.
 */
function renderList() {
  notesList.replaceChildren();
  // replaceChildren = clear list of already rendered notes

  for (const note of notes) {
    const item = document.createElement('li');
    item.className = 'note-item';
    if (note.id === selectedId) {
      item.classList.add('selected');
    }

    const title = document.createElement('div');
    title.className = 'note-title';
    title.textContent = getTitle(note.text);

    const meta = document.createElement('div');
    meta.className = 'note-meta';
    meta.textContent = parseDate(note.created_at).toLocaleDateString('en-GB');

    item.append(title, meta);
    item.addEventListener('click', () => selectNote(note.id));
    notesList.append(item);
  }
}

/*
 * selectNote
 * Action: the user clicked a note in the list.
 * 1) change the state (selectedId)
 * 2) fill the right side with the note (read-only: the API has no
 *    update endpoint, only GET and POST)
 * 3) redraw the list so the highlight moves
 */
function selectNote(id) {
  const note = notes.find((n) => n.id === id);
  if (!note) return;

  selectedId = id;
  noteText.value = note.text;
  noteText.readOnly = true;
  noteDate.textContent = parseDate(note.created_at).toLocaleString('en-GB');
  saveBtn.hidden = true;
  clearError();
  renderList();
}

/*
 * startNewNote
 * Action: the "New note" button (also runs once at startup).
 * Same scheme as selectNote: selectedId becomes null, the right side
 * turns into an empty editable field with the Save button, the list
 * is redrawn so nothing is highlighted.
 */
function startNewNote() {
  selectedId = null;
  noteText.value = '';
  noteText.readOnly = false;
  noteDate.textContent = '';
  saveBtn.hidden = false;
  updateSaveButton();
  clearError();
  renderList();
  noteText.focus();
}

/*
 * loadNotes
 * Talks to the API: GET /api/notes. A non-2xx status (404, 500) is
 * turned into an error with a readable message; otherwise the JSON
 * array becomes the new "notes" state and the list is redrawn.
 * The server is the source of truth: we reload the list instead of
 * building notes locally, because id and created_at are created by
 * the database.
 */
async function loadNotes() {
  const response = await fetch('/api/notes');

  if (!response.ok) {
    throw new Error('GET /api/notes failed: ' + response.status);
  }

  notes = await response.json();
  renderList();
}

/*
 * saveNote
 * Talks to the API: POST /api/notes with {"text": "..."}.
 * The Content-Type header tells the server the body is JSON (our PHP
 * reads php://input, not $_POST).
 * Success is exactly 201: reload the list and open the created note
 * (its id comes from the response). Any other status shows the
 * "error" field from the API's {"error": "..."} format.
 * The Save button is disabled while the request runs and enabled
 * again in "finally", which runs on success and on error.
 */
async function saveNote() {
  clearError();
  saveBtn.disabled = true;

  try {
    const response = await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: noteText.value }),
    });
    const data = await response.json();

    if (response.status !== 201) {
      showError(data.error || 'Something went wrong');
      return;
    }

    await loadNotes();
    selectNote(data.id);
  } catch (err) {
    showError('Request failed: ' + err.message);
  } finally {
    updateSaveButton();
  }
}

// ---------------------------------------------------------------
// Wiring and startup.
// addEventListener("click", fn) means "call fn when clicked"
// (the function name goes without parentheses: we pass the function
// itself, we do not call it now).
// On start: load notes, then open an empty new note; if loading
// fails, show the error text under the field.
// ---------------------------------------------------------------
newNoteBtn.addEventListener('click', startNewNote);
saveBtn.addEventListener('click', saveNote);
noteText.addEventListener('input', updateSaveButton);

loadNotes()
  .then(startNewNote)
  .catch((err) => showError(err.message));