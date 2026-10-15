-- Seed data for Library Book Reservation System
-- Loaded by setupdev.bat only when the books table is empty (idempotent).
--
-- Book A (id=1) has 3 copies and 0 reservations — matches the challenge's
-- "Book A has 3 copies" example used in trick-logic tests.
--
-- Dates use SQLite datetime() so they are always in the future at load time.

INSERT INTO books (id, title, author, total_copies, available_copies) VALUES
(1, 'Book A',                                'Author A',                                    3, 3),
(2, 'Clean Code',                            'Robert C. Martin',                            2, 1),
(3, 'Introduction to Algorithms',            'Cormen, Leiserson, Rivest, Stein',            1, 0),
(4, 'Designing Data-Intensive Applications', 'Martin Kleppmann',                            4, 4),
(5, 'Python Crash Course',                   'Eric Matthes',                                3, 1);

-- Reservations that keep available_copies consistent with the rows above:
--   Book 2: 1 reservation  → available = 2 - 1 = 1
--   Book 3: 1 reservation  → available = 1 - 1 = 0
--   Book 5: 2 reservations → available = 3 - 2 = 1
INSERT INTO reservations (book_id, user_name, expires_at) VALUES
(2, 'alice', datetime('now', '+6 days')),
(3, 'bob',   datetime('now', '+5 days')),
(5, 'carol', datetime('now', '+4 days')),
(5, 'dave',  datetime('now', '+3 days'));
