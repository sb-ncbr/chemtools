from unittest.mock import AsyncMock, patch

from services.worker_service import WorkerService
from tools.chargefw2.tool import ChargeFW2Tool


async def run_calculation(*args, data, **kwargs):
    worker_service = WorkerService(AsyncMock(), AsyncMock(), chargefw2=ChargeFW2Tool(AsyncMock(), AsyncMock()))
    await worker_service.run_calculation_async(**data)


async def test_get_chargefw2_modes(client):
    response = await client.get("/chargefw2")
    assert response.status_code == 200
    assert response.json() == {"available_modes": ["info", "charges", "best-parameters", "suitable-methods"]}


@patch("services.message_broker_service.MessageBrokerService._send_message")
async def test_calculation_flow(send_message: AsyncMock, client):
    send_message.side_effect = run_calculation
    with open("src/tests/test_data/1tqn.cif", "rb") as file:
        response = await client.post(
            "/files",
            files=[
                ("files", ("test_file.cif", file, "application/octet-stream")),
            ],
        )
    assert response.status_code == 200

    [file_hash] = response.json()["files"]

    response = await client.post(
        "/chargefw2/charges",
        json={
            "input_data": {
                "input_file": file_hash,
            }
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["info"] == "Calculation task enqueued"
    token = response_json["token"]

    response = await client.get(f"/calculation/{token}")
    assert response.status_code == 200
    assert response.json()["id"] == token
