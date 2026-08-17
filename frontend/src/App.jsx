import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [expenses, setExpenses] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editAmount, setEditAmount] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  async function handleSubmit(e) {
    e.preventDefault();

    const response = await fetch('http://localhost:8000/expenses/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title,
        amount: Number(amount),
        category
      })
    });

    const newExpense = await response.json();

    setExpenses([...expenses, newExpense]);

    setTitle('');
    setAmount('');
    setCategory('');
  }

  async function handleDelete(expenseId) {
    const response = await fetch(
      `http://localhost:8000/expenses/${expenseId}`,
      {
        method: 'DELETE'
      }
    );

    if (response.ok) {
      setExpenses(
        expenses.filter((expense) => expense.id !== expenseId)
      );
    }
  }

  useEffect(() => {
    async function fetchExpenses() {
      const response = await fetch(
        'http://localhost:8000/expenses/'
      );

      const expensesData = await response.json();
      setExpenses(expensesData);
    }

    fetchExpenses();
  }, []);

  const totalSpent = expenses.reduce(
    (total, expense) => total + expense.amount,
    0
  );

  const expenseCount = expenses.length;

  const averageExpense =
    expenseCount > 0 ? totalSpent / expenseCount : 0;
  
  const categories = ['All', ...new Set(expenses.map((e) => e.category))];
  const filteredExpenses = expenses.filter((expense) => {
    const matchesSearchTerm = expense.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || expense.category === selectedCategory;

    return matchesSearchTerm && matchesCategory;
  });

  return (
    <div className="App">
      <div className="container">

        <div className="top-bar">
  <div className="header">
    <h1>Expense Tracker</h1>
    <p>Track and manage your everyday expenses.</p>
  </div>

  <div className="dashboard">
    <div className="stat-card">
      <span>Total</span>
      <strong>${totalSpent.toFixed(2)}</strong>
    </div>

    <div className="stat-card">
      <span>Expenses</span>
      <strong>{expenseCount}</strong>
    </div>

    <div className="stat-card">
      <span>Average</span>
      <strong>${averageExpense.toFixed(2)}</strong>
    </div>
  </div>
</div>

        <section className="card">
          <h2>Add Expense</h2>

          <form className="expense-form" onSubmit={handleSubmit}>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              type="text"
              placeholder="Title"
              required
            />

            <input
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              type="number"
              step="0.01"
              placeholder="Amount"
              required
            />

            <input
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              type="text"
              placeholder="Category"
              required
            />

            <button className="add-button" type="submit">
              Add Expense
            </button>
          </form>
        </section>

       <section className="card">
  <h2>Your Expenses</h2>

  <div className="expense-filters">
    <input
      type="text"
      placeholder="Search expenses..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
    />

    <select
      value={selectedCategory}
      onChange={(e) => setSelectedCategory(e.target.value)}
    >
      {categories.map((category) => (
        <option key={category} value={category}>
          {category}
        </option>
      ))}
    </select>
  </div>

  {expenses.length === 0 ? (
    <div className="empty">
      No expenses yet. Add your first expense above.
    </div>
  ) : filteredExpenses.length === 0 ? (
    <div className="empty">
      No expenses match your search or filter.
    </div>
  ) : (
    <div className="expenses-list">
      {filteredExpenses.map((expense) => (
        <div className="expense" key={expense.id}>

          {editingId === expense.id ? (
            <form
              className="edit-form"
              onSubmit={async (e) => {
                e.preventDefault();

                const response = await fetch(
                  `http://localhost:8000/expenses/${expense.id}`,
                  {
                    method: 'PUT',
                    headers: {
                      'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                      title: editTitle,
                      amount: Number(editAmount),
                      category: editCategory
                    })
                  }
                );

                const updatedExpense = await response.json();

                setExpenses(
                  expenses.map((e) =>
                    e.id === expense.id
                      ? updatedExpense
                      : e
                  )
                );

                setEditingId(null);
              }}
            >
              <input
                value={editTitle}
                onChange={(e) =>
                  setEditTitle(e.target.value)
                }
                type="text"
                required
              />

              <input
                value={editAmount}
                onChange={(e) =>
                  setEditAmount(e.target.value)
                }
                type="number"
                step="0.01"
                required
              />

              <input
                value={editCategory}
                onChange={(e) =>
                  setEditCategory(e.target.value)
                }
                type="text"
                required
              />

              <button
                className="save-button"
                type="submit"
              >
                Save
              </button>

              <button
                className="cancel-button"
                type="button"
                onClick={() => setEditingId(null)}
              >
                Cancel
              </button>
            </form>
          ) : (
            <>
              <div className="expense-info">
                <h3>{expense.title}</h3>

                <p className="expense-amount">
                  ${expense.amount.toFixed(2)}
                </p>

                <p>
                  Category: {expense.category}
                </p>
              </div>

              <div className="expense-actions">
                <button
                  className="edit-button"
                  onClick={() => {
                    setEditingId(expense.id);
                    setEditTitle(expense.title);
                    setEditAmount(expense.amount);
                    setEditCategory(expense.category);
                  }}
                >
                  Edit
                </button>

                <button
                  className="delete-button"
                  onClick={() => handleDelete(expense.id)}
                >
                  Delete
                </button>
              </div>
            </>
          )}

        </div>
      ))}
    </div>
  )}
</section>

      </div>
    </div>
  );
}

export default App;
