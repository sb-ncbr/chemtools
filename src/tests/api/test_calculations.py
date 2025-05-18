# import uuid

# async def test_calculation_flow(client):
#     response = await client.post("/files", json={})
#     assert response.status_code == 201
#     pipeline_id = response.json()["id"]

#     pipeline = await client.get(f"/pipeline/{pipeline_id}")
#     assert pipeline.status_code == 200
#     assert pipeline.json()["id"] == pipeline_id
