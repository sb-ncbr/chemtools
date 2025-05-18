import io
import uuid

from services.file_storage_service import FileStorageService


async def test_file_user_upload_download(client):
    user_id = str(uuid.uuid4())
    file_content1 = b"test content 1"
    file_content2 = b"test content 2"
    response = await client.post(
        "/files",
        files=[
            ("files", ("test1.txt", io.BytesIO(file_content1), "text/plain")),
            ("files", ("test2.txt", io.BytesIO(file_content2), "text/plain")),
        ],
        data={"user_id": user_id},
    )

    assert response.status_code == 200
    file_hash1, file_hash2 = response.json()["files"]

    assert FileStorageService.get_file_hash(file_content1) == file_hash1
    assert FileStorageService.get_file_hash(file_content2) == file_hash2

    response = await client.get(
        "/files",
        params={
            "user_id": user_id,
            "files": [file_hash1, file_hash2],
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].endswith(".zip")


async def test_upload_download_one_file(client):
    pass
