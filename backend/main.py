from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import (
    create_tables, 
    create_expense, 
    get_expenses, 
    get_expense_by_id,
    update_expense,
    delete_expense,
    get_expense_summary,
    get_expenses_by_category
)

from pydantic import BaseModel, Field


class Expense(BaseModel):
    title: str = Field(min_length=1)
    amount: float = Field(ge=0)
    category: str = Field(min_length=1)
    notes: str | None = None
class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    notes: str | None = None
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/expenses/", response_model=ExpenseResponse, status_code=201)
def add_expense(expense: Expense):
    expense_id = create_expense(
        expense.title, 
        expense.amount, 
        expense.category, 
        expense.notes
    )
    return ExpenseResponse(
        id=expense_id, 
        title=expense.title, 
        amount=expense.amount, 
        category=expense.category,
        notes=expense.notes
    )

@app.get("/expenses/summary")
def expense_summary():
    summary = get_expense_summary()
    return summary

@app.get("/expenses/by-category")
def expense_by_category(min_amount: float | None = None, category: str | None = None):
    return get_expenses_by_category(min_amount, category)

@app.get("/expenses/", response_model=list[ExpenseResponse])
def list_expenses(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort : str = Query("id"),
    order : str = Query("asc")
):
    return get_expenses(limit, offset, sort, order)

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
        expense.category,
        expense.notes
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
        category=expense.category,
        notes=expense.notes
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

