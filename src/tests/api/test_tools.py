async def test_get_chargefw2_modes(client):
    response = await client.get("/chargefw2")
    assert response.status_code == 200
    assert response.json() == {"available_modes": ["info", "charges", "best-parameters", "suitable-methods"]}
