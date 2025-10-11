from fastapi import FastAPI, HTTPException
from datetime import date, datetime
from typing import List
from pydantic import BaseModel
import db_helper

app = FastAPI()
print("Running server.py from:", __file__)


# ------------------------------
# Pydantic models
# ------------------------------
class Expense(BaseModel):
    amount: float
    category: str
    notes: str


class DateRange(BaseModel):
    start_date: str
    end_date: str


# ------------------------------
# Endpoints
# ------------------------------
@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expenses(expense_date: date):
    """Fetch all expenses for a given date."""
    expenses = db_helper.fetch_expenses_for_date(expense_date)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expense]):
    """Delete and re-insert expenses for a date (update)."""
    db_helper.delete_expenses_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)
    return {"message": "Expenses updated successfully"}


@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    """Aggregate expense totals by category within a date range."""
    try:
        start_date = datetime.strptime(date_range.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(date_range.end_date, "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")

    data = db_helper.fetch_expense_summary(start_date, end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database.")

    total = sum([row["total"] for row in data]) if data else 0

    breakdown = {}
    for row in data:
        percentage = (row["total"] / total) * 100 if total != 0 else 0
        breakdown[row["category"]] = {
            "total": row["total"],
            "percentage": percentage
        }

    return breakdown


@app.get("/")
def root():
    return {"message": "Expense Manager API is running!"}
