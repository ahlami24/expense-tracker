from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import (
    create_tables, 
    create_expense, 
    get_expenses, 
    get_expense_by_id,
    update_expense,
    delete_expense
)

from pydantic import BaseModel


class Expense(BaseModel):
    title: str
    amount: float
    category: str
class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/expenses/", response_model=ExpenseResponse)
def add_expense(expense: Expense):
    expense_id = create_expense(
        expense.title, 
        expense.amount, 
        expense.category
    )
    return ExpenseResponse(
        id=expense_id, 
        title=expense.title, 
        amount=expense.amount, 
        category=expense.category
    )

@app.get("/expenses/", response_model=list[ExpenseResponse])
def list_expenses():
    return get_expenses()


@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int):
    expense = get_expense_by_id(expense_id)
    if expense is None:
        raise HTTPException(
            status_code=404, 
            detail="Expense not found"
        )
    return ExpenseResponse(**expense)

@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense_endpoint(expense_id: int, expense: Expense):
    updated_rows = update_expense(
        expense_id, 
        expense.title, 
        expense.amount, 
        expense.category
    )
    if updated_rows == 0:
        raise HTTPException(
            status_code=404, 
            detail="Expense not found"
        )
    return ExpenseResponse(
        id=expense_id, 
        title=expense.title, 
        amount=expense.amount, 
        category=expense.category
    )

@app.delete("/expenses/{expense_id}")
def delete_expense_endpoint(expense_id: int):
    deleted_rows = delete_expense(expense_id)
    if deleted_rows == 0:
        raise HTTPException(
            status_code=404, 
            detail="Expense not found"
        )
    return {"detail": "Expense deleted successfully"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)