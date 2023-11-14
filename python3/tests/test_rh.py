# tests/test_rh.py
from src.rh import Portfolio
from src.rh import Stock

def test_create_stock():
    portfolio = Portfolio()
    portfolio.createStock("AMD")
    assert portfolio.positions["AMD"].symbol == "AMD"
    assert type(portfolio.positions["AMD"]) == Stock
def test_get_stock():
    portfolio = Portfolio()
    portfolio.createStock("AMD")
    stock = portfolio.getStock("AMD")
    assert type(stock) == Stock
    assert stock.symbol == "AMD"
