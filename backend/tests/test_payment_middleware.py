import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_contract_create_list_execute(client: AsyncClient):
    create_payload = {
        "name": "Student MCC",
        "contract_type": "mcc_limit",
        "parameters": {"allowed_mcc": ["5411", "5812"], "blocked_mcc": ["4121"], "applicable_cards": ["all"]},
        "description": "Limit student spend",
    }
    create_resp = await client.post("/api/v1/payment-middleware/contracts", json=create_payload)
    assert create_resp.status_code == 200
    contract = create_resp.json()

    list_resp = await client.get("/api/v1/payment-middleware/contracts")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Allowed MCC
    exec_resp = await client.post(
        "/api/v1/payment-middleware/contracts/execute",
        json={
            "contract_id": contract["contract_id"],
            "purchase_info": {
                "mcc": "5411",
                "cost": 100.0,
                "merchant_id": "merchant_001",
                "card_number": "1234567812345678",
            },
        },
    )
    assert exec_resp.status_code == 200
    assert exec_resp.json()["allowed"] is True

    # Blocked MCC
    exec_resp_blocked = await client.post(
        "/api/v1/payment-middleware/contracts/execute",
        json={
            "contract_id": contract["contract_id"],
            "purchase_info": {
                "mcc": "4121",
                "cost": 50.0,
                "merchant_id": "taxi_01",
                "card_number": "1234567812345678",
            },
        },
    )
    assert exec_resp_blocked.status_code == 200
    assert exec_resp_blocked.json()["allowed"] is False


@pytest.mark.asyncio
async def test_purchase_with_contract_and_balance_checks(client: AsyncClient):
    # Create amount limit contract
    resp = await client.post(
        "/api/v1/payment-middleware/contracts",
        json={
            "name": "Limit 500",
            "contract_type": "amount_limit",
            "parameters": {"max_amount": 500, "applicable_cards": ["1234567812345678"]},
        },
    )
    contract_id = resp.json()["contract_id"]

    # Fails by contract
    fail_resp = await client.post(
        f"/api/v1/payment-middleware/process-purchase-with-contract?contract_id={contract_id}",
        json={
            "mcc": "5411",
            "cost": 600.0,
            "merchant_id": "store_01",
            "card_number": "1234567812345678",
        },
    )
    assert fail_resp.status_code == 400
    assert "Contract violation" in fail_resp.json()["detail"]

    # Passes when under limit and funds available
    ok_resp = await client.post(
        f"/api/v1/payment-middleware/process-purchase-with-contract?contract_id={contract_id}",
        json={
            "mcc": "5411",
            "cost": 200.0,
            "merchant_id": "store_02",
            "card_number": "1234567812345678",
        },
    )
    assert ok_resp.status_code == 200
    data = ok_resp.json()
    assert data["status"] == "completed"
    assert data["amount"] == 200.0


@pytest.mark.asyncio
async def test_deposit_and_balance(client: AsyncClient):
    deposit_resp = await client.post(
        "/api/v1/payment-middleware/deposit",
        json={"card_number": "1111222233334444", "amount": 5000},
    )
    assert deposit_resp.status_code == 200

    balance_resp = await client.get("/api/v1/payment-middleware/balance/1111222233334444")
    assert balance_resp.status_code == 200
    balance = balance_resp.json()
    assert balance["balance"] >= 5000

    tx_resp = await client.get("/api/v1/payment-middleware/transactions/1111222233334444")
    assert tx_resp.status_code == 200
    assert len(tx_resp.json()) >= 1
