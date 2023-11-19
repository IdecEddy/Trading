# tests/test_rh.py
from src.rh import Portfolio
from src.rh import Stock
from src.rh import CSVParser

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
def test_CSV_obj_creation():
    portfolio = Portfolio()
    portfolio.setCSVObj("test.csv", ['GRPN', 'FIT', 'ATVI'])
    assert type(portfolio.csvParser) == CSVParser
def test_get_portfolio():
    portfolio = Portfolio()
    portfolio.setCSVObj("test.csv", ['GRPN', 'FIT', 'ATVI'])
    portfolio.getProfile()
    assert type(portfolio.csvParser) == CSVParser
    assert type(portfolio.getStock("AMD")) == Stock
