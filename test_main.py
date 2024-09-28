import random
from string import ascii_letters

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

credentials = {
    "username": "johndoe",
    "password": "123456"
}


def get_x_token():
    """ will call token endpoint and return JWT """
    response = client.post("/token", data=credentials)
    assert response.status_code == 200
    return response.json()["access_token"]


def get_header():
    """ will return a valid header with auth """
    return {"Authorization": f"Bearer {get_x_token()}"}


def test_add_stock():
    company_name = ''.join(random.choices(ascii_letters, k=8))
    ticker = ''.join(random.choices(ascii_letters, k=4))
    current_price = random.randint(10, 100)
    daily_change_percent = random.randint(-10, 100)
    stock_turnover = random.randint(100, 1000)
    new_stock = {
        "company_name": company_name,
        "ticker": ticker,
        "current_price": current_price,
        "daily_change_percent": daily_change_percent,
        "stock_turnover": stock_turnover
    }
    response = client.post(
        "/add_stock",
        headers=get_header(),
        json=new_stock
    )
    assert response.status_code == 201
    result: dict = response.json()
    result.pop("id")
    assert result == new_stock


def test_unauthorized_add_stock():
    response = client.post(
        "/add_stock",
        json={
            "company_name": "string",
            "ticker": "string",
            "current_price": 0,
            "daily_change_percent": 0,
            "stock_turnover": 0
        }
    )
    assert response.status_code == 401


def test_get_stock_list():
    response = client.get("/stock_list/", headers=get_header())
    assert response.status_code == 200
    assert type(response.json()) == list


def test_create_get_update_delete_stock():
    response = client.post(
        "/add_stock",
        headers=get_header(),
        json={
            "company_name": "fake_name",
            "ticker": "fkt",
            "current_price": 15,
            "daily_change_percent": 5,
            "stock_turnover": 500
        }
    )
    assert response.status_code == 201
    response = client.get("/get_stock/fkt", headers=get_header())
    assert response.status_code == 200
    result = response.json()
    new_data = {
            "company_name": "real_name",
            "ticker": "rln",
            "current_price": 10,
            "daily_change_percent": 10,
            "stock_turnover": 1000}
    response = client.put(f'/update_stock/{result["id"]}', headers=get_header(), json=new_data)
    assert response.status_code == 200
    new_data["id"] = result["id"]
    result = response.json()
    assert result == new_data
    response = client.delete(f"/delete_stock/{result['ticker']}", headers=get_header())
    assert response.status_code == 200
    assert response.json() == {"message": f"stock {result['ticker']} got deleted successfully."}
    # trying to re-delete it
    response = client.delete(f"/delete_stock/{result['ticker']}", headers=get_header())
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
