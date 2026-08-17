import sqlite3
def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        conn.commit()

def create_expense(title: str, amount: float, category: str):
    with get_db_connection() as conn:
        cursor = conn.execute('''
            INSERT INTO expenses (title, amount, category)
            VALUES (?, ?, ?)
        ''', (title, amount, category))
        conn.commit()
        return cursor.lastrowid

def get_expenses():
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM expenses')
        expenses = cursor.fetchall()
        return [dict(expense) for expense in expenses]

def get_expense_by_id(expense_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
        expense = cursor.fetchone()
        return dict(expense) if expense else None

def update_expense(
        expense_id: int, 
        title: str, amount: 
        float, category: str
    ):
    with get_db_connection() as conn:
        cursor = conn.execute('''
            UPDATE expenses
            SET title = ?, amount = ?, category = ?
            WHERE id = ?
        ''', (title, amount, category, expense_id))
        conn.commit()
        return cursor.rowcount

def delete_expense(expense_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        return cursor.rowcount
    