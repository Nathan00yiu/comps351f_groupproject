Comps351f group 26
project files
Demo link in demolink.txt
others are project program

# Library Borrowing System

A database-driven library management system designed to handle book circulation, user account management, overdues, and status tracking.

---

## Key Features

* **User Authentication:** Account registration and login system for users.
* **Book Circulation:** Borrowing and returning mechanisms with tracking for overdue fines.
* **Catalog Management:** Search and query system to check detailed book availability and status.
* **Borrowing Limits:** User-level restrictions on maximum allowed book loans.

---

## Database Architecture

The system utilizes a structured relational database model with the following core entities:

### 1. Book (`Book table`)

Stores catalog details and current physical state.

* `bookID` (PK): `str` — Unique identifier for each book.
* `name`: `str` — Title of the book.
* `author`: `str` — Author(s) of the book.
* `publish year`: `int` — Year of publication.
* `intro`: `str` — Book description/synopsis.
* `statusID` (FK): `int` — References book status (e.g., available, borrowed, damaged, lost).

### 2. User (`User table`)

Manages patron profiles and account limits.

* `userID` (PK): `str` — Unique user identifier.
* `username`: `str` — Display/login name.
* `password`: `str` — Account password.
* `email`: `str` — User email address.
* `phone_number`: `str` — Contact phone number.
* `bookBorrowLimit`: `int` — Maximum number of books the user can borrow simultaneously.

### 3. Borrow (`Borrow table`)

Tracks active borrowing transactions, due dates, and fine calculations.

---

## Getting Started

### Prerequisites

* Database Management System (e.g., MySQL / PostgreSQL / SQLite)
* Backend runtime (e.g., Python / Java / Node.js) depending on your implementation stack

### Installation & Setup

1. **Clone the Repository:**
```bash
git clone https://github.com/Nathan00yiu/comps351f_groupproject.git
cd comps351f_groupproject

```


2. **Database Configuration:**
* Execute your SQL schema scripts to create the `Book`, `User`, and `Borrow` tables.
* Update the database configuration file with your database credentials.


3. **Run the Application:**
```bash
# Add your main application launch command here

```



---

## License

Distributed under the MIT License. See `LICENSE` for more information.
