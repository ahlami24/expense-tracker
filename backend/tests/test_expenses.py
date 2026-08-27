from unicodedata import category

from fastapi.testclient import TestClient
from main import app
import os
import pytest
import database
import sqlite3

client = TestClient(app)

def create_test_expense(title, amount, category):
    response = client.post("/expenses/", json={
        "title": title,
        "amount": amount,
        "category": category
    })

    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def sample_expenses(test_database):
    expenses = [
        database.create_expense("Lunch", 10.0, "Food"),
        database.create_expense("Bus Ticket", 3.0, "Transport"),
        database.create_expense("Dinner", 7.0, "Food"),
        database.create_expense("Pizza", 20.0, "Food")
    ]
    
@pytest.mark.parametrize(
    "min_amount, expected_count", 
    [
        (7,3),
        (10, 2), 
        (20,1)
    ]
)
def test_min_amount_filter(sample_expenses, min_amount, expected_count):
    response = client.get(f"/expenses/by-category?min_amount={min_amount}")
    assert response.status_code == 200
    food = next(
        item for item in response.json()
        if item["category"] == "Food")
    assert food["expense_count"] == expected_count

def test_create_expense(test_database):
    expense = {
        "title": "Test Expense",
        "amount": 100.0,
        "category": "Test Category",
        "notes": "Test notes"
    }
    response = client.post("/expenses/", json=expense)

    assert response.status_code == 201
    assert response.json()["title"] == "Test Expense"
    assert response.json()["amount"] == 100.0
    assert response.json()["category"] == "Test Category"
    assert response.json()["notes"] == "Test notes"

def test_list_expenses_empty(test_database):
    response = client.get("/expenses/")
    assert response.status_code == 200
    assert response.json() == []

def test_list_expenses_with_data(test_database):
    create_test_expense("Pizza", 20.0, "Food")
    create_test_expense("Bus", 5.0, "Transport")
    create_test_expense("Movie", 15.0, "Entertainment")

    response = client.get("/expenses/")
    assert response.status_code == 200
    assert len(response.json()) == 3
    expenses = response.json()

    assert expenses[0]["title"] == "Pizza"
    assert expenses[0]["amount"] == 20.0
    assert expenses[0]["category"] == "Food"

    assert expenses[1]["title"] == "Bus"
    assert expenses[1]["amount"] == 5.0
    assert expenses[1]["category"] == "Transport"

    assert expenses[2]["title"] == "Movie"
    assert expenses[2]["amount"] == 15.0
    assert expenses[2]["category"] == "Entertainment"

def test_get_expense_by_id(test_database):
    response = client.post("/expenses/", json={
        "title": "Lunch", 
        "amount": 12.0, 
        "category": "Food"
    })
    expense_id = response.json()["id"]

    response = client.get(f"/expenses/{expense_id}")
    assert response.status_code == 200
    expense = response.json()
    assert expense["title"] == "Lunch"
    assert expense["amount"] == 12.0
    assert expense["category"] == "Food"

def test_get_expense_not_found(test_database):
    response = client.get("/expenses/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}

def test_update_expense(test_database):
    create_response = client.post("/expenses/", json={
        "title": "Pizza",
        "amount": 20.0,
        "category": "Food"
    })

    expense_id = create_response.json()["id"]

    update_response = client.put(f"/expenses/{expense_id}", json={
        "title": "Burger",
        "amount": 30.0,
        "category": "Food"
    })

    assert update_response.status_code == 200

    updated_expense = update_response.json()

    assert updated_expense["id"] == expense_id
    assert updated_expense["title"] == "Burger"
    assert updated_expense["amount"] == 30.0
    assert updated_expense["category"] == "Food"

    get_response = client.get(f"/expenses/{expense_id}")

    assert get_response.status_code == 200

    saved_expense = get_response.json()

    assert saved_expense["title"] == "Burger"
    assert saved_expense["amount"] == 30.0
    assert saved_expense["category"] == "Food"

def test_update_expense_not_found(test_database):
    response = client.put("/expenses/999", json={
        "title": "Non-existent",
        "amount": 0.0,
        "category": "None"
    })
    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}

def test_delete_expense(test_database):
    create_response = create_test_expense("Lunch", 10.0, "Food")

    expense_id = create_response["id"]

    delete_response = client.delete(f"/expenses/{expense_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"detail": "Expense deleted successfully"}

    get_response = client.get(f"/expenses/{expense_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Expense not found"}

def test_delete_expense_not_found(test_database):
    response = client.delete("/expenses/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}

def test_expenses_summary(test_database):
    create_test_expense("Lunch", 10.0, "Food")
    create_test_expense("Bus", 3.0, "Transport")
    create_test_expense("Dinner", 20.0, "Food")

    response = client.get("/expenses/summary/")
    assert response.status_code == 200
    summary = response.json()

    assert summary["expense_count"] == 3
    assert summary["total_spent"] == 33.0
    assert summary["average_expense"] == pytest.approx(33/3)

def test_expenses_with_category(sample_expenses):
    
    response = client.get("/expenses/by-category?category=Food")
    assert response.status_code == 200
    expenses = response.json()

    assert len(expenses) == 1
    food = expenses[0]
    assert food["category"] == "Food"
    assert food["expense_count"] == 3
    assert food["total_spent"] == 37.0
    assert food["average_expense"] == pytest.approx(37/3)

def test_expenses_by_min_amount(sample_expenses):
  
    response = client.get("/expenses/by-category?min_amount=10")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    food = next(
        item for item in expenses 
        if item["category"] == "Food")

    assert food["expense_count"] == 2
    assert food["total_spent"] == 30.0
    assert food["average_expense"] == 15.0

def test_expenses_by_category_and_min_amount(sample_expenses):

    response = client.get("/expenses/by-category?min_amount=10&category=Food")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    food = expenses[0]

    assert food["category"] == "Food"
    assert food["expense_count"] == 2
    assert food["total_spent"] == 30.0
    assert food["average_expense"] == 15.0

def test_expenses_by_category_no_results(test_database):
    response = client.get("/expenses/by-category?category=Entertainment")
    assert response.status_code == 200
    assert response.json() == []

def test_expenses_sort_by_amount_desc(sample_expenses):
    response = client.get("/expenses/?sort=amount&order=desc")
    assert response.status_code == 200
    expenses = response.json()

    assert len(expenses) == 4
    assert expenses[0]["amount"] == 20.
    assert expenses[1]["amount"] == 10.0
    assert expenses[2]["amount"] == 7.0
    assert expenses[3]["amount"] == 3.0

def test_expenses_sort_by_amount_asc(sample_expenses):
    response = client.get("/expenses/?sort=amount&order=asc")
    assert response.status_code == 200
    expenses = response.json()

    assert len(expenses) == 4
    assert expenses[0]["amount"] == 3.0
    assert expenses[1]["amount"] == 7.0
    assert expenses[2]["amount"] == 10.0
    assert expenses[3]["amount"] == 20.0

def test_list_expenses_with_pagination(test_database):
    for i in range(15):
        client.post("/expenses/", json={
            "title": f"Expense {i+1}", 
            "amount": (i+1) * 10.0, 
            "category": "Test"
        })

    response = client.get("/expenses/?limit=5&offset=5")
    assert response.status_code == 200
    expenses = response.json()

    assert len(expenses) == 5
    assert expenses[0]["title"] == "Expense 6"
    assert expenses[0]["amount"] == 60.0
    assert expenses[4]["title"] == "Expense 10"
    assert expenses[4]["amount"] == 100.0

def test_list_expenses_pagination_with_sorting(test_database):
    for i in range(15):
        client.post("/expenses/", json={
            "title": f"Expense {i+1}", 
            "amount": (i+1) * 10.0, 
            "category": "Test"
        })

    response = client.get("/expenses/?sort=amount&order=desc&limit=5&offset=5")
    assert response.status_code == 200
    expenses = response.json()

    assert len(expenses) == 5
    assert expenses[0]["title"] == "Expense 10"
    assert expenses[0]["amount"] == 100.0
    assert expenses[4]["title"] == "Expense 6"
    assert expenses[4]["amount"] == 60.0

def test_list_expenses_same_amount_uses_id_as_tiebreaker(test_database):
    create_test_expense("Pizza", 20.0, "Food")
    create_test_expense("Coffee", 20.0, "Beverage")
    create_test_expense("Bus", 20.0, "Transport")
    create_test_expense("Laptop", 20.0, "Electronics")

    response = client.get(
        "/expenses/?sort=amount&order=asc"
    )

    assert response.status_code == 200

    expenses = response.json()

    assert expenses[0]["title"] == "Pizza"
    assert expenses[1]["title"] == "Coffee"
    assert expenses[2]["title"] == "Bus"
    assert expenses[3]["title"] == "Laptop"

def test_isolation_one(test_database):
    create_test_expense("Expense A", 10.0, "Category A")
    response = client.get("/expenses/")
    assert len(response.json()) == 1

def test_isolation_two(test_database):
    response = client.get("/expenses/")
    assert response.json() == []

def test_create_expense_negative_amount(test_database):
    response = client.post("/expenses/", json={
        "title": "Invalid expense",
        "amount": -10,
        "category": "Food"
    })
    assert response.status_code == 422

def test_create_expense_empity_title(test_database):
    response = client.post("/expenses/", json={
        "title" : "",
        "amount": 10,
        "category" : "Food"
    })
    assert response.status_code == 422

def test_create_expense_empity_category(test_database):
    response = client.post("/expenses/", json={
        "title" : "Lounch",
        "amount" : 10,
        "category": ""
    })
    assert response.status_code == 422

def test_update_expense_negative_amount(test_database):
    create_response = client.post("/expenses", json={
        "title" : "Pizza",
        "amount" : 20,
        "category" : "Food"
    })
    expense_id = create_response.json()["id"]

    response = client.put(f"/expenses/{expense_id}", json={
        "title": "Invalid expense",
        "amount": -10,
        "category": "Food"
    })
    assert response.status_code == 422

def test_update_expense_empity_title(test_database):
    create_response = client.post("/expenses", json={
        "title" : "Pizza",
        "amount" : 20,
        "category" : "Food"
    })
    expense_id = create_response.json()["id"]

    response = client.put(f"/expenses/{expense_id}", json={
        "title" : "",
        "amount": 10,
        "category" : "Food"
    })
    assert response.status_code == 422

def test_update_expense_empity_category(test_database):
    create_response = client.post("/expenses", json={
        "title" : "Pizza",
        "amount" : 20,
        "category" : "Food"
    })
    expense_id = create_response.json()["id"]
    response = client.put(f"/expenses/{expense_id}", json={
        "title" : "Lounch",
        "amount" : 10,
        "category": ""
    })
    assert response.status_code == 422

def test_database_rejects_negative_amount(test_database):
    with pytest.raises(sqlite3.IntegrityError):
        database.create_expense(
            "Invalid Expense",
            -10.0,
            "Food"
        )

def test_list_expenses_invalid_sort_uses_id(test_database):
    client.post("/expenses/", json={
        "title": "Pizza",
        "amount": 20.0,
        "category": "Food"
    })

    client.post("/expenses/", json={
        "title": "Coffee",
        "amount": 5.0,
        "category": "Food"
    })

    response = client.get("/expenses/?sort=banana&order=asc")

    assert response.status_code == 200
    expenses = response.json()

    assert expenses[0]["id"] < expenses[1]["id"]

def test_list_expenses_invalid_order_uses_asc(test_database):
    client.post("/expenses/", json={
        "title": "Pizza",
        "amount": 20.0,
        "category": "Food"
    })

    client.post("/expenses/", json={
        "title": "Coffee",
        "amount": 5.0,
        "category": "Food"
    })

    response = client.get("/expenses/?sort=amount&order=banana")

    assert response.status_code == 200
    expenses = response.json()

    assert expenses[0]["amount"] == 5.0
    assert expenses[1]["amount"] == 20.0