import sqlite3
import os
from datetime import datetime, timedelta
from faker import Faker
import random


DB_PATH = "library.db"
NUM_BOOKS = 100000
MIN_USERS = 7000
MAX_USERS = 9000
BOOK_BORROW_LIMIT = 6
BORROW_DAYS = 7
FINE_PER_DAY = 5.125
BORROW_WEIGHTS = [5, 10, 15, 20, 40, 15, 5]
DISPLAY_ROWS = 10
LOST_PROBABILITY = 0.05  

fake = Faker()

def initialize_database(db_path=DB_PATH, drop_tables=True):
    """
    初始化資料庫
    :param db_path: 資料庫檔案路徑
    :param drop_tables: True 表示刪除所有表並重建，False 表示刪除檔案並重建
    """
    if not drop_tables and os.path.exists(db_path):
        print(f"Deleting existing database file: {db_path}")
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    if drop_tables and os.path.exists(db_path):
        print("Dropping all existing tables...")
        cursor.execute("DROP TABLE IF EXISTS Fine")
        cursor.execute("DROP TABLE IF EXISTS Borrow")
        cursor.execute("DROP TABLE IF EXISTS User")
        cursor.execute("DROP TABLE IF EXISTS Book")
        cursor.execute("DROP TABLE IF EXISTS BookStatus")

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BookStatus (
            statusID INTEGER PRIMARY KEY,
            statusDetail TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Book (
            bookID TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            author TEXT NOT NULL,
            publish_year INTEGER,
            intro TEXT,
            statusID INTEGER,
            FOREIGN KEY (statusID) REFERENCES BookStatus(statusID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            UserID TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            bookBorrowLimit INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Borrow (
            BorrowID TEXT PRIMARY KEY,
            UserID TEXT NOT NULL,
            BookID TEXT NOT NULL,
            datetime_borrowed DATETIME NOT NULL,
            except_return_date DATETIME NOT NULL,
            is_returned BOOLEAN NOT NULL DEFAULT 0,
            is_overdue BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (UserID) REFERENCES User(UserID),
            FOREIGN KEY (BookID) REFERENCES Book(bookID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Fine (
            FineID TEXT PRIMARY KEY,
            BorrowID TEXT NOT NULL,
            fine_amount REAL NOT NULL,
            is_paid BOOLEAN NOT NULL DEFAULT 0,
            overdue_days INTEGER NOT NULL,
            FOREIGN KEY (BorrowID) REFERENCES Borrow(BorrowID)
        )
    ''')

    
    cursor.execute("INSERT OR IGNORE INTO BookStatus (statusID, statusDetail) VALUES (?, ?)", (1, "Available"))
    cursor.execute("INSERT OR IGNORE INTO BookStatus (statusID, statusDetail) VALUES (?, ?)", (2, "Borrowed"))
    cursor.execute("INSERT OR IGNORE INTO BookStatus (statusID, statusDetail) VALUES (?, ?)", (3, "Lost"))

    
    print(f"Generating {NUM_BOOKS} books...")
    books = []
    for i in range(NUM_BOOKS):
        book_id = f"B{i:05d}"
        book_name = " ".join(fake.catch_phrase().split()[:3])
        
        status_id = 3 if random.random() < LOST_PROBABILITY else 1
        books.append((
            book_id,
            book_name,
            fake.name(),
            fake.year(),
            fake.paragraph(nb_sentences=2),
            status_id
        ))
    cursor.executemany("INSERT OR IGNORE INTO Book (bookID, name, author, publish_year, intro, statusID) VALUES (?, ?, ?, ?, ?, ?)", books)

    
    num_users = random.randint(MIN_USERS, MAX_USERS)
    print(f"Generating {num_users + 1} users (including default account)...")
    users = []
    default_user = (
        "U00000",
        "default@example.com",
        "12345678",
        "123",
        "123",
        BOOK_BORROW_LIMIT
    )
    users.append(default_user)
    cursor.execute("INSERT OR IGNORE INTO User (UserID, email, phone_number, username, password, bookBorrowLimit) VALUES (?, ?, ?, ?, ?, ?)", default_user)

    for i in range(1, num_users + 1):
        user_id = f"U{i:05d}"
        username = fake.unique.user_name()
        email = fake.unique.email()
        users.append((
            user_id,
            email,
            fake.phone_number()[:8],
            username,
            fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True),
            BOOK_BORROW_LIMIT
        ))
    cursor.executemany("INSERT OR IGNORE INTO User (UserID, email, phone_number, username, password, bookBorrowLimit) VALUES (?, ?, ?, ?, ?, ?)", users[1:])

    
    print("Generating borrow records...")
    borrows = []
    fines = []
    borrow_id_counter = 0
    current_date = datetime.now()

    
    available_books = [book for book in books if book[5] == 1]

    for user in users:
        user_id = user[0]
        num_borrowed = random.choices(range(BOOK_BORROW_LIMIT + 1), weights=BORROW_WEIGHTS, k=1)[0]
        
        borrowed_books = random.sample(available_books, min(num_borrowed, len(available_books)))
        for book in borrowed_books:
            borrow_id = f"BOR{borrow_id_counter:05d}"
            borrow_id_counter += 1
            book_id = book[0]
            
            cursor.execute("UPDATE Book SET statusID = 2 WHERE bookID = ?", (book_id,))
            
            book_index = next(i for i, b in enumerate(available_books) if b[0] == book_id)
            available_books[book_index] = (book[0], book[1], book[2], book[3], book[4], 2)
            
            borrow_date = fake.date_time_between(start_date="-60d", end_date="now")
            return_date = borrow_date + timedelta(days=BORROW_DAYS)
            is_overdue = 1 if current_date > return_date else 0
            borrows.append((
                borrow_id,
                user_id,
                book_id,
                borrow_date.strftime("%Y-%m-%d %H:%M:%S"),
                return_date.strftime("%Y-%m-%d %H:%M:%S"),
                0,  
                is_overdue
            ))
            if is_overdue:
                fine_id = f"F{borrow_id_counter:05d}"
                overdue_days = (current_date - return_date).days
                fine_amount = overdue_days * FINE_PER_DAY
                fines.append((fine_id, borrow_id, fine_amount, 0, overdue_days))
    cursor.executemany("INSERT OR IGNORE INTO Borrow (BorrowID, UserID, BookID, datetime_borrowed, except_return_date, is_returned, is_overdue) VALUES (?, ?, ?, ?, ?, ?, ?)", borrows)
    cursor.executemany("INSERT OR IGNORE INTO Fine (FineID, BorrowID, fine_amount, is_paid, overdue_days) VALUES (?, ?, ?, ?, ?)", fines)

    
    conn.commit()

    
    print(f"\nVerifying database content (showing first {DISPLAY_ROWS} rows per table):")
    cursor.execute(f"SELECT * FROM Book LIMIT {DISPLAY_ROWS}")
    print("Book table:")
    [print(i) for i in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM User LIMIT {DISPLAY_ROWS}")
    print("User table:")
    [print(i) for i in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM Borrow LIMIT {DISPLAY_ROWS}")
    print("Borrow table:")
    [print(i) for i in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM Fine LIMIT {DISPLAY_ROWS}")
    print("Fine table:")
    [print(i) for i in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM BookStatus LIMIT {DISPLAY_ROWS}")
    print("BookStatus table:")
    [print(i) for i in cursor.fetchall()]

    conn.close()
    print(f"Database '{db_path}' initialized successfully with {NUM_BOOKS} books and {num_users + 1} users!")

if __name__ == "__main__":
    try:
        initialize_database(DB_PATH, drop_tables=True)
    except ImportError:
        print("Please install the 'faker' package: pip install faker")