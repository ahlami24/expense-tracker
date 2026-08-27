import sqlite3
DATABASE_PATH = 'expenses.db'
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def migrate_add_amount_check():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE expenses_new (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                category TEXT NOT NULL
            )
        ''')

        conn.execute('''
            INSERT INTO expenses_new (id, title, amount, category)
            SELECT id, title, amount, category
            FROM expenses
        ''')

        conn.execute('DROP TABLE expenses')

        conn.execute('''
            ALTER TABLE expenses_new
            RENAME TO expenses
        ''')

        conn.commit()

def create_tables():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                category TEXT NOT NULL,
                notes TEXT
            )
        ''')
        conn.commit()

def create_expense(title: str, amount: float, category: str, notes: str | None = None):
    with get_db_connection() as conn:
        cursor = conn.execute('''
            INSERT INTO expenses (title, amount, category, notes)
            VALUES (?, ?, ?, ?)
        ''', (title, amount, category, notes))
        conn.commit()
        return cursor.lastrowid

def get_expenses(limit=10, offset=0, sort="id", order="asc"):
    with get_db_connection() as conn:

        allowed_sort_fields = {
            "id": "id",
            "title": "title",
            "amount": "amount",
            "category": "category"
        }
        sort_column = allowed_sort_fields.get(sort, "id")

        if order.lower() not in ["asc", "desc"]:
            order = "asc"
        query = f"""
            SELECT *
            FROM expenses
            ORDER BY {sort_column} {order.upper()}, id ASC
            LIMIT ? OFFSET ?
        """
        cursor = conn.execute(
            query,
            (limit, offset)
        )

        return [dict(row) for row in cursor.fetchall()]

def get_expense_by_id(expense_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM expenses 
            WHERE id = ?
        """, (expense_id,))
        expense = cursor.fetchone()
        return dict(expense) if expense else None

def update_expense(
        expense_id: int, 
        title: str, amount: 
        float, category: str, 
        notes: str | None = None
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

def get_expense_summary():
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT COUNT(*), SUM(amount), AVG(amount)
            FROM expenses
        """)

        row = cursor.fetchone()

    return {
        "expense_count": row[0],
        "total_spent": row[1],
        "average_expense": row[2]
    }

def get_expenses_by_category(min_amount: float | None = None, category: str | None = None):
    with get_db_connection() as conn:
        conditions = []
        parameters = []

        if category:
            conditions.append("category = ?")
            parameters.append(category)
        if min_amount is not None:
            conditions.append("amount >= ?")
            parameters.append(min_amount)
                    
        query = "SELECT category, COUNT(*), SUM(amount), AVG(amount) FROM expenses"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " GROUP BY category"
        cursor = conn.execute(query, parameters)
        rows = cursor.fetchall()

    return [
        {
            "category": row[0],
            "expense_count": row[1],
            "total_spent": row[2],
            "average_expense": row[3]
        }
        for row in rows
    ]
