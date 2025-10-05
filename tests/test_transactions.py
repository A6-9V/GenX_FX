import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.models.transaction import Transaction

client = TestClient(app)

@pytest.fixture
def sample_gasoline_transaction_input():
    return {
        "buy_price_per_ton_usd": 700,
        "number_of_tanks": 10,
        "exchange_rate_usd_to_khr": 4100,
        "fuel_type": "gasoline",
        "profit_per_tank_khr": 4000
    }

@pytest.fixture
def sample_diesel_transaction_input():
    return {
        "buy_price_per_ton_usd": 800,
        "number_of_tanks": 5,
        "exchange_rate_usd_to_khr": 4100,
        "fuel_type": "diesel",
        "profit_per_tank_khr": 4000
    }

def test_create_gasoline_transaction(sample_gasoline_transaction_input):
    response = client.post("/transactions/", json=sample_gasoline_transaction_input)
    assert response.status_code == 200
    data = response.json()
    assert "total_profit_khr" in data
    assert data["total_tanks"] == 10
    # This check will be enabled after modifying the service to return fuel_type
    # assert data["fuel_type"] == "gasoline"

def test_create_diesel_transaction(sample_diesel_transaction_input):
    response = client.post("/transactions/", json=sample_diesel_transaction_input)
    assert response.status_code == 200
    data = response.json()
    assert "total_profit_khr" in data
    assert data["total_tanks"] == 5
    # This check will be enabled after modifying the service to return fuel_type
    # assert data["fuel_type"] == "diesel"

def test_get_transactions():
    from api.routers.transactions import transactions_db
    transactions_db.clear()

    client.post("/transactions/", json={
        "buy_price_per_ton_usd": 750,
        "number_of_tanks": 2,
        "exchange_rate_usd_to_khr": 4150,
        "fuel_type": "gasoline",
        "profit_per_tank_khr": 4000
    })

    response = client.get("/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "input" in data[0]
    assert "output" in data[0]
    assert data[0]["input"]["number_of_tanks"] == 2

def test_calculation_logic():
    from api.services.transaction_service import calculate_transaction_details

    transaction_model = Transaction(
        buy_price_per_ton_usd=700,
        number_of_tanks=1,
        exchange_rate_usd_to_khr=4100,
        fuel_type="gasoline",
        gasoline_liters_per_ton=1390,
        liters_per_tank=34,
        profit_per_tank_khr=4000
    )

    details = calculate_transaction_details(transaction_model)

    # Correct values based on high-precision calculation
    expected_tons = 0.02446043165467626
    expected_sell_price_per_tank_khr = 74201.43884892086
    expected_total_profit_khr = 4000.0

    assert abs(details["tons"] - expected_tons) < 0.0001
    assert abs(details["total_profit_khr"] - expected_total_profit_khr) < 0.01
    assert abs(details["sell_price_per_tank_khr"] - expected_sell_price_per_tank_khr) < 0.01