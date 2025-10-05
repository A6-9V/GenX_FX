from pydantic import BaseModel
from typing import Optional

class Transaction(BaseModel):
    gasoline_liters_per_ton: float = 1390.0
    diesel_liters_per_ton: float = 1190.0
    liters_per_tank: float = 34.0
    buy_price_per_ton_usd: float
    number_of_tanks: int
    exchange_rate_usd_to_khr: float
    profit_per_liter_khr: float = 300.0
    profit_per_tank_khr: float = 4000.0
    fuel_type: str  # 'gasoline' or 'diesel'