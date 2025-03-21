BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "counts" (
	"term"	INTEGER,
	"document"	INTEGER,
	"count"	INTEGER DEFAULT 0,
	PRIMARY KEY("term","document"),
	FOREIGN KEY("document") REFERENCES "document"("id"),
	FOREIGN KEY("term") REFERENCES "terms"("id")
);
CREATE TABLE IF NOT EXISTS "document" (
	"id"	INTEGER,
	"path"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "terms" (
	"id"	INTEGER,
	"term"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
