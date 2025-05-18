import io
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from api.enums import MoleculeFileExtensionEnum, MoleculeRepoSiteEnum
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

    assert FileStorageService.get_file_hash(file_content1) == file_hash1.removesuffix(".txt")
    assert FileStorageService.get_file_hash(file_content2) == file_hash2.removesuffix(".txt")

    response = await client.get(
        "/files",
        params={
            "user_id": user_id,
            "file_names": [file_hash1, file_hash2],
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].endswith(".zip")


async def test_upload_download_one_file(client):
    file_content = b"test content"
    response = await client.post(
        "/files",
        files=[
            ("files", ("test1.txt", io.BytesIO(file_content), "text/plain")),
        ],
        data={},
    )

    assert response.status_code == 200
    [file_hash] = response.json()["files"]

    assert FileStorageService.get_file_hash(file_content) == file_hash.removesuffix(".txt")

    response = await client.get(
        "/files",
        params={
            "file_names": [file_hash],
        },
    )
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].endswith(".txt")
    assert response.content == file_content


@pytest.mark.parametrize(
    "site", [MoleculeRepoSiteEnum.alphafold, MoleculeRepoSiteEnum.rcsb_pdb, MoleculeRepoSiteEnum.pubchem]
)
async def test_supported_site_extensions(client, site):
    response = await client.get(
        "/supported-site-extensions",
        params={"site": site},
    )
    assert response.status_code == 200
    assert response.json() == site.get_site_extensions()


@patch("clients.fetcher_client.OnlineFileFetcherClient._download", new_callable=AsyncMock)
async def test_online_file_force_cache(mocked_download: AsyncMock, client):
    file_content = b"molecule data"
    mocked_download.return_value = file_content
    response = await client.get(
        "/online-file",
        params={
            "molecule_id": "test_id",
            "site": MoleculeRepoSiteEnum.alphafold,
            "extension": MoleculeFileExtensionEnum.cif,
            "force_download": True,
        },
    )
    assert response.status_code == 200

    response = await client.get(
        "/online-file",
        params={
            "molecule_id": "test_id",
            "site": MoleculeRepoSiteEnum.alphafold,
            "extension": MoleculeFileExtensionEnum.cif,
            "force_download": True,
        },
    )
    assert response.status_code == 200
    assert mocked_download.call_count == 2
    assert response.json() == {"file": f"{FileStorageService.get_file_hash(file_content)}.cif", "cached": False}


@patch("clients.fetcher_client.OnlineFileFetcherClient._download", new_callable=AsyncMock)
async def test_online_file_cached(mocked_download: AsyncMock, client):
    file_content = b"molecule data"
    mocked_download.return_value = file_content
    response = await client.get(
        "/online-file",
        params={
            "molecule_id": "test_id",
            "site": MoleculeRepoSiteEnum.alphafold,
            "extension": MoleculeFileExtensionEnum.cif,
            "force_download": False,
        },
    )
    assert response.status_code == 200

    response = await client.get(
        "/online-file",
        params={
            "molecule_id": "test_id",
            "site": MoleculeRepoSiteEnum.alphafold,
            "extension": MoleculeFileExtensionEnum.cif,
            "force_download": False,
        },
    )
    assert response.status_code == 200
    assert mocked_download.call_count == 1
    assert response.json() == {"file": f"{FileStorageService.get_file_hash(file_content)}.cif", "cached": True}


async def test_user_files(client):
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
    assert FileStorageService.get_file_hash(file_content1) == file_hash1.removesuffix(".txt")
    assert FileStorageService.get_file_hash(file_content2) == file_hash2.removesuffix(".txt")
    response = await client.get(
        "/user/files",
        params={
            "user_id": user_id,
        },
    )
    assert response.status_code == 200
    user_file1, user_file2 = response.json()
    assert user_file1["file_name"] == "test1.txt"
    assert user_file1["file_name_hash"] == file_hash1
    assert user_file2["file_name"] == "test2.txt"
    assert user_file2["file_name_hash"] == file_hash2

    assert user_file1["user_id"] == user_id
    assert user_file2["user_id"] == user_id
