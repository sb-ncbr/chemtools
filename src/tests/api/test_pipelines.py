import uuid


async def test_create_pipeline(client):
    response = await client.post("/pipeline", json={})
    assert response.status_code == 201
    pipeline_id = response.json()["id"]

    pipeline = await client.get(f"/pipeline/{pipeline_id}")
    assert pipeline.status_code == 200
    assert pipeline.json()["id"] == pipeline_id


async def test_create_pipeline_user(client):
    user_token = str(uuid.uuid4())

    response = await client.post("/pipeline", json={"user_id": user_token})
    assert response.status_code == 201

    pipeline = await client.get(f"/user/{user_token}/pipelines")
    assert pipeline.status_code == 200
    assert pipeline.json()[0]["user_id"] == user_token
