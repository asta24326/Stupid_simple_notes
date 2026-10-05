# Simple example:

# creating table
CREATE TABLE notes (
	id SERIAL PRIMARY KEY,
	text TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# syntax:
- CREATE TABLE [notes] = create a table with name [notes]
- [id] SERIAL PRIMARY KEY = 
	column name [id];
	SERIAL = autoincrementing number (id++);
	PRIMARY KEY = unique key (can not be two rows with same id);
- [text] TEXT NOT NULL = 
	column name [text];
	TEXT = text data type;
	NOT NULL = mandatory (NULL is not acceptable);
- [created_at] TIMESTAMP DEFAULT CURRENT_TIMESTAMP = 
	column name [created_at];
	TIMESTAMP = date and time;
	DEFAULT = default value;
	CURRENT_TIMESTAMP = current time DB(at the moment of creation);

# inserting data to the table
INSERT INTO notes (text) VALUES ('Hello world!');

# syntax:
- INSERT INTO = paste a row in table
- [notes] = name of the table
- (text) = specify in which columns we're inserting 
	([id] and  [created_at] inserts data automatically)
- VALUES (...) = values to insert

# data query from tables
SELECT * FROM notes;

# syntax:
- SELECT = select (request)
- * = all columns
- FROM [notes] = from table with name [notes]

# sorted data query
SELECT * FROM notes ORDER BY created_at DESC LIMIT 10;

# syntax:
- ORDER BY [column_name] DESC = order by [column_name] descending
- LIMIT 10 = limit, take only 10 first rows

# delete table
DROP TABLE notes;

# syntax:
- DROP = delete
- TABLE [notes] = table with name [notes]