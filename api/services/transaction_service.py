from api.models.transaction import Transaction

def calculate_transaction_details(transaction: Transaction):
    if transaction.fuel_type == 'gasoline':
        liters_per_ton = transaction.gasoline_liters_per_ton
    else:
        liters_per_ton = transaction.diesel_liters_per_ton

    # 1. Calculate total volume based on number of tanks
    total_liters = transaction.number_of_tanks * transaction.liters_per_tank

    # 2. Convert volume to tons
    tons = total_liters / liters_per_ton

    # 3. Calculate total buy cost in USD
    total_buy_cost_usd = tons * transaction.buy_price_per_ton_usd

    # 4. Calculate buy price per liter and per tank in USD
    buy_price_per_liter_usd = total_buy_cost_usd / total_liters if total_liters > 0 else 0
    buy_price_per_tank_usd = total_buy_cost_usd / transaction.number_of_tanks if transaction.number_of_tanks > 0 else 0

    # 5. Calculate selling price in KHR
    buy_price_per_tank_khr = buy_price_per_tank_usd * transaction.exchange_rate_usd_to_khr
    sell_price_per_tank_khr = buy_price_per_tank_khr + transaction.profit_per_tank_khr
    sell_price_per_liter_khr = sell_price_per_tank_khr / transaction.liters_per_tank if transaction.liters_per_tank > 0 else 0

    # 6. Calculate total revenue and profit in KHR
    total_revenue_khr = sell_price_per_tank_khr * transaction.number_of_tanks
    total_buy_khr = total_buy_cost_usd * transaction.exchange_rate_usd_to_khr
    total_profit_khr = total_revenue_khr - total_buy_khr

    # 7. Calculate profit per liter (as a derived value)
    calculated_profit_per_liter_khr = transaction.profit_per_tank_khr / transaction.liters_per_tank if transaction.liters_per_tank > 0 else 0

    return {
        "tons": tons,
        "total_liters": total_liters,
        "total_tanks": transaction.number_of_tanks,
        "buy_price_per_ton_usd": transaction.buy_price_per_ton_usd,
        "buy_price_per_liter_usd": buy_price_per_liter_usd,
        "buy_price_per_tank_usd": buy_price_per_tank_usd,
        "buy_price_per_tank_khr": buy_price_per_tank_khr,
        "sell_price_per_tank_khr": sell_price_per_tank_khr,
        "sell_price_per_liter_khr": sell_price_per_liter_khr,
        "total_revenue_khr": total_revenue_khr,
        "total_buy_khr": total_buy_khr,
        "total_profit_khr": total_profit_khr,
        "calculated_profit_per_liter_khr": calculated_profit_per_liter_khr,
        "input_profit_per_liter_khr": transaction.profit_per_liter_khr,
        "input_profit_per_tank_khr": transaction.profit_per_tank_khr,
        "fuel_type": transaction.fuel_type
    }