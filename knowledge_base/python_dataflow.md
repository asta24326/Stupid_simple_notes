# Python-бэкенд: кто кого вызывает и как это видно в коде

> Это про Python-версию (`backend/app/`, FastAPI).
> Сейчас в `docker-compose` работает PHP: `nginx → PHP-FPM → index.php`.
> Python-версия запускается отдельно: `make run` → `uvicorn app.main:app --reload`
> на `http://127.0.0.1:8000` (nginx и фронтенд в этой цепочке не участвуют).

Номера строк указаны на момент написания (ветка `13-logging`) и могут сдвигаться.

---

## 1. Общая картина

```
клиент (curl / Swagger /docs)
   │  HTTP
   ▼
Uvicorn ──────────────► app (FastAPI-объект, main.py:45)
                          │ роутинг по пути и методу
                          ▼
                     handlers/notes.py      (HTTP-слой)
                          │ service.xxx(...)
                          ▼
                     services/notes.py      (бизнес-правила)
                          │ self._repository.xxx(...)   self._unit_of_work (with)
                          ▼                              ▼
              repositories/db/notes.py        repositories/db/unit_of_work.py
                          │ cursor.execute(...)          │ connection.commit()/rollback()
                          └───────────┬──────────────────┘
                                      ▼
                             psycopg.Connection ──► PostgreSQL
```

Две важные вещи:

- **Вызовы вниз** (хендлер → сервис → репозиторий) видны в коде как обычные вызовы методов.
- **Связи, которых в коде не видно** (кто подставил сервис, кто поймал исключение, кто закрыл соединение) делает FastAPI. Они описаны в разделе 4.

---

## 2. Кто кого вызывает (с привязкой к строкам)

| Кто вызывает                    | Что вызывает                                                        | Где в коде                                                                                             |
| ------------------------------------------ | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| Uvicorn                                    | `app` (ASGI-приложение)                                            | `main.py:45` `app = FastAPI()`                                                                             |
| FastAPI                                    | функцию-хендлер по маршруту                            | `handlers/notes.py:20-59` (декораторы `@router.get/post/put/delete`)                             |
| FastAPI                                    | `provide_notes_service()` вместо `get_notes_service()`               | `main.py:50` + `handlers/notes.py:17`                                                                      |
| хендлер `list_notes`              | `service.list_notes(limit, offset)`                                          | `handlers/notes.py:31`                                                                                       |
| хендлер `get_note`                | `service.get_note(note_id)`                                                  | `handlers/notes.py:38`                                                                                       |
| хендлер `create_note`             | `service.create_note(body.text)`                                             | `handlers/notes.py:45`                                                                                       |
| хендлер `update_note`             | `service.update_note(note_id, body.text)`                                    | `handlers/notes.py:52`                                                                                       |
| хендлер `delete_note`             | `service.delete_note(note_id)`                                               | `handlers/notes.py:59`                                                                                       |
| `NotesService.create_note`               | `self._validate_text(text)`                                                  | `services/notes.py:35`                                                                                       |
| `NotesService.create_note`               | `with self._unit_of_work:` → `self._repository.create_note(text)`         | `services/notes.py:36-37`                                                                                    |
| `NotesService.update_note`               | `_validate_text`, `with unit_of_work`, `repository.update_note`          | `services/notes.py:41-44`                                                                                    |
| `NotesService.delete_note`               | `with unit_of_work`, `repository.delete_note`                              | `services/notes.py:51-52`                                                                                    |
| `NotesService.get_note` / `list_notes` | `self._repository.get_note` / `list_notes` (без `with`: чтение) | `services/notes.py:24, 28`                                                                                   |
| `with`-блок (Python)                 | `UnitOfWorkInterface.__enter__` / `__exit__`                               | `unit_of_work_interface.py:8, 12`                                                                            |
| `__exit__`                               | `self.commit()` или `self.rollback()`                                   | `unit_of_work_interface.py:17-19`                                                                            |
| `DbUnitOfWork.commit/rollback`           | `self._connection.commit()` / `.rollback()`                                | `repositories/db/unit_of_work.py:15, 19`                                                                     |
| `DbNotesRepository.*`                    | `cursor.execute(SQL)` и `self._row_to_note(row)`                          | `repositories/db/notes.py`                                                                                   |
| FastAPI (при ошибке)              | обработчик из `handlers/errors.py`                               | регистрация: `handlers/errors.py:32-35`, вызов `register_error_handlers` в `main.py:46` |

---

## 3. Сборка при старте (выполняется один раз при импорте `main.py`)

```python
settings = Settings()                                   # main.py:24  читает env (host, port, db, user, password)
app = FastAPI()                                         # main.py:45  создаёт приложение
register_error_handlers(app)                            # main.py:46  «исключение X → ответ Y»
app.dependency_overrides[get_notes_service] = provide_notes_service   # main.py:50  подмена заглушки
app.include_router(router)                              # main.py:53  подключает маршруты /api/notes
```

Порядок: настройки → приложение → обработчики ошибок → подмена зависимости → маршруты.

---

## 4. То, что не видно в коде: «невидимые» вызовы

### 4.1 Кто вызывает хендлер и откуда берётся `service`

В хендлере (`handlers/notes.py:36`) написано:

```python
def get_note(note_id: int, service: NotesServiceDependency):
```

Нигде в коде нет строки `get_note(...)` с реальными аргументами. Их собирает FastAPI:

- `note_id: int` берётся из пути `/{note_id}` и приводится к `int`;
- `body: NoteIn` берётся из тела запроса и проверяется по схеме (`handlers/schemas.py`);
- `limit` и `offset` берутся из query-строки с проверкой `ge/le` (`handlers/notes.py:23-24`);
- `service: NotesServiceDependency`. Это `Annotated[NotesService, Depends(get_notes_service)]` (`handlers/notes.py:17`).
  Читается так: «чтобы получить `service`, вызови `get_notes_service`».

### 4.2 Заглушка и подмена

```python
# handlers/notes.py:11-13
def get_notes_service() -> NotesService:
    raise NotImplementedError          # реально никогда не выполнится

# main.py:50
app.dependency_overrides[get_notes_service] = provide_notes_service
```

Когда FastAPI хочет вызвать `get_notes_service`, он смотрит в `dependency_overrides`, находит замену и вызывает `provide_notes_service`.
Хендлер при этом не знает про `main.py`, поэтому цикла импортов нет.

### 4.3 Генератор с `yield`: setup и cleanup

```python
# main.py:28-42
def provide_notes_service() -> Iterator[NotesService]:
    connection = psycopg.connect(...)                 # ДО yield: setup (до вызова хендлера)
    try:
        repository = DbNotesRepository(connection)
        unit_of_work = DbUnitOfWork(connection)       # то же соединение, что у репозитория
        yield NotesService(repository, unit_of_work)  # ← FastAPI берёт это значение и отдаёт хендлеру
    finally:
        connection.close()                            # ПОСЛЕ ответа (или после ошибки): cleanup
```

Обрати внимание: **репозиторий и unit of work создаются на одном `connection`**.
Благодаря этому `commit()` из `DbUnitOfWork` фиксирует именно то, что записал `DbNotesRepository`.

### 4.4 Конструкторы: где слои соединяются

| Конструктор                     | Что принимает             | Где вызывается |
| ------------------------------------------ | ------------------------------------- | --------------------------- |
| `DbNotesRepository(connection)`          | открытое соединение | `main.py:38`              |
| `DbUnitOfWork(connection)`               | то же соединение        | `main.py:39`              |
| `NotesService(repository, unit_of_work)` | репозиторий + UoW          | `main.py:40`              |

Сервис в аннотациях требует **интерфейсы** (`services/notes.py:17`: `NotesRepositoryInterface`, `UnitOfWorkInterface`), а не `Db...`-классы.
Конкретные классы подставляются только в `main.py`. Так сервис можно тестировать с фейками из `tests/fakes.py`.

### 4.5 `with self._unit_of_work:` — вызовы, которых не видно

```python
with self._unit_of_work:                     # services/notes.py:36
    return self._repository.create_note(text)
```

Python сам вызывает:

1. `__enter__()` при входе (`unit_of_work_interface.py:8`). Он ничего не делает, транзакция в psycopg стартует с первого запроса.
2. `__exit__(...)` при выходе из блока (`unit_of_work_interface.py:12`):
   - без исключения → `self.commit()`;
   - с исключением → `self.rollback()`, исключение летит дальше (метод возвращает `None`, поэтому не «глотает» его).

`commit` и `rollback` абстрактные. Реальные реализации лежат в `DbUnitOfWork` (`repositories/db/unit_of_work.py`).

### 4.6 Исключения: кто поймает

В сервисе пишется `raise NoteNotFoundError(...)` (`services/notes.py:30, 47, 54`), но `try/except` в хендлере нет.
Исключение поднимается до FastAPI, а он ищет обработчик среди зарегистрированных в `handlers/errors.py:30-35`:

| Исключение                    | Обработчик        | Ответ                       |
| --------------------------------------- | --------------------------- | -------------------------------- |
| `EmptyTextError`                      | `handle_bad_text`         | 400                              |
| `TextTooLongError`                    | `handle_bad_text`         | 400                              |
| `NoteNotFoundError`                   | `handle_not_found`        | 404                              |
| любое другое (`Exception`) | `handle_unexpected_error` | 500, `"Internal server error"` |

Тело ошибки: `{"detail": "..."}` (формат как у стандартных ошибок FastAPI).

### 4.7 Превращение `Note` в JSON

Хендлер возвращает `Note` (dataclass из `models/note.py`), а не словарь.
Декоратор `@router.post("", response_model=NoteOut, ...)` говорит FastAPI: «преобразуй результат в `NoteOut` и сериализуй в JSON».
Это работает благодаря `ConfigDict(from_attributes=True)` в `NoteOut` (`handlers/schemas.py`): pydantic читает поля `id`, `text`, `created_at` прямо из атрибутов объекта.

---

## 5. Полный путь одного запроса: `POST /api/notes {"text": "hi"}`

| № | Кто                    | Что делает                                                                                                            | Где                                 |
| -- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------- |
| 1  | Uvicorn                   | принимает HTTP, разбирает его, вызывает `app`                                                   | —                                     |
| 2  | FastAPI                   | находит маршрут `POST /api/notes` → `create_note`                                                           | `handlers/notes.py:42-43`            |
| 3  | FastAPI                   | проверяет тело по `NoteIn`; при ошибке формы отвечает 422 и дальше не идёт | `handlers/schemas.py`                |
| 4  | FastAPI                   | для `service` вызывает `provide_notes_service` (подмена)                                                 | `main.py:50`                         |
| 5  | `provide_notes_service` | открывает соединение, создаёт repository + UoW + service, доходит до `yield`              | `main.py:29-40`                      |
| 6  | FastAPI                   | вызывает `create_note(body, service)`                                                                                | `handlers/notes.py:44`               |
| 7  | хендлер            | `service.create_note("hi")`                                                                                                  | `handlers/notes.py:45`               |
| 8  | сервис              | `_validate_text("hi")`: пусто или длиннее 10000 → исключение                                       | `services/notes.py:35, 56`           |
| 9  | сервис              | `with self._unit_of_work:` → `__enter__`                                                                                  | `services/notes.py:36`               |
| 10 | сервис              | `self._repository.create_note("hi")`                                                                                         | `services/notes.py:37`               |
| 11 | репозиторий    | `INSERT ... RETURNING id, text, created_at`                                                                                  | `repositories/db/notes.py:48-60`     |
| 12 | репозиторий    | `_row_to_note(row)` → `Note(...)`                                                                                         | `repositories/db/notes.py:90`        |
| 13 | сервис              | `return` внутри `with` → `__exit__` → `commit()`                                                               | `unit_of_work_interface.py:17-18`    |
| 14 | `DbUnitOfWork`          | `self._connection.commit()`                                                                                                  | `repositories/db/unit_of_work.py:15` |
| 15 | хендлер            | возвращает `Note`                                                                                                  | `handlers/notes.py:46`               |
| 16 | FastAPI                   | `Note` → `NoteOut` → JSON, статус 201                                                                              | `handlers/notes.py:42`               |
| 17 | FastAPI                   | возобновляет генератор → `finally` → `connection.close()`                                           | `main.py:41-42`                      |
| 18 | Uvicorn                   | отправляет ответ клиенту                                                                                 | —                                     |

### Если на шаге 8 пустой текст

1. `_validate_text` бросает `EmptyTextError`.
2. До `with` дело не доходит: в БД ничего не записывается, `commit` и `rollback` не вызываются.
3. Исключение проходит через хендлер к FastAPI → `handle_bad_text` → ответ 400.
4. `finally` в `provide_notes_service` закрывает соединение.

### Если `PUT /api/notes/999`, а такой заметки нет

1. Валидация текста проходит.
2. `with unit_of_work`: репозиторий возвращает `None` (`UPDATE` не затронул ни одной строки).
3. Сервис бросает `NoteNotFoundError` **внутри** `with` (`services/notes.py:47`).
4. `__exit__` видит исключение → `rollback()`, исключение летит дальше.
5. FastAPI → `handle_not_found` → 404.
6. `finally` закрывает соединение.

---

## 6. Кто за что отвечает (коротко)

| Слой        | Знает про                                                                     | Не знает про                   |
| --------------- | ------------------------------------------------------------------------------------- | ---------------------------------------- |
| handlers        | HTTP, FastAPI, схемы запросов и ответов, сервис            | SQL, psycopg                             |
| services        | правила (валидация, NotFound), интерфейсы repository и UoW | HTTP, SQL                                |
| repositories/db | SQL, psycopg, модель `Note`                                                   | правила, commit/rollback          |
| unit_of_work    | commit и rollback соединения                                               | какие данные записаны |
| main.py         | всё: собирает слои вместе                                        | —                                       |

Правило: зависимости идут вниз и только на интерфейсы; конкретные классы связываются **только** в `main.py`.

---

## 7. Как это проверять в тестах

- Сервис: `tests/test_notes_service.py` создаёт `NotesService` с фейками из `tests/fakes.py`, без БД.
- Хендлеры: `tests/test_notes_handler.py` подменяет `get_notes_service` через `dependency_overrides` на сервис с фейками.
- Unit of work: `tests/test_unit_of_work.py`.
