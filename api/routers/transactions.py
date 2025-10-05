from fastapi import APIRouter, Depends
from typing import List
from api.models.transaction import Transaction
from api.services.transaction_service import calculate_transaction_details

router = APIRouter()

# In-memory storage for transactions (for demonstration purposes)
transactions_db: List[dict] = []

@router.post("/", response_model=dict)
def create_transaction(transaction: Transaction):
    """
    Calculates transaction details based on input and returns the result.
    The result is also stored in-memory.
    """
    transaction_details = calculate_transaction_details(transaction)

    # Add the original input and the calculated details to our "database"
    stored_transaction = {
        "input": transaction.model_dump(),
        "output": transaction_details
    }
    transactions_db.append(stored_transaction)

    return transaction_details

@router.get("/", response_model=List[dict])
def get_transactions():
    """
    Retrieves the list of all processed transactions.
    """
    return transactions_db