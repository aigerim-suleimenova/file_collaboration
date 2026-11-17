"""File endpoints and per-owner access control (S3 replaced by an in-memory fake)."""

import pytest

from .conftest import auth_header


@pytest.fixture()
def a_headers(user_a, access_token):
    return auth_header(access_token(user_a))


@pytest.fixture()
def b_headers(user_b, access_token):
    return auth_header(access_token(user_b))


@pytest.fixture()
def uploaded(client, fake_s3, a_headers):
    res = client.post(
        "/api/v1/files/upload",
        headers=a_headers,
        files={"file": ("notes.txt", b"hello world", "text/plain")},
    )
    assert res.status_code == 200, res.text
    return res.json()


def test_upload_stores_object_and_metadata(uploaded, fake_s3):
    assert uploaded["filename"] == "notes.txt"
    assert uploaded["file_size"] == 11
    assert fake_s3.objects[uploaded["s3_key"]] == b"hello world"


def test_owner_can_list_and_get(client, uploaded, a_headers):
    listed = client.get("/api/v1/files/", headers=a_headers)
    assert listed.status_code == 200
    assert [f["id"] for f in listed.json()] == [uploaded["id"]]

    got = client.get(f"/api/v1/files/{uploaded['id']}", headers=a_headers)
    assert got.status_code == 200
    assert got.json()["filename"] == "notes.txt"


def test_owner_can_read_content(client, uploaded, a_headers):
    res = client.get(f"/api/v1/files/{uploaded['id']}/content", headers=a_headers)
    assert res.status_code == 200
    assert res.content == b"hello world"


def test_owner_can_update_quill_content(client, uploaded, a_headers):
    res = client.post(
        f"/api/v1/files/{uploaded['id']}/update-quill-content",
        headers=a_headers,
        data={"quill_content": "<p>edited</p>"},
    )
    assert res.status_code == 200
    got = client.get(f"/api/v1/files/{uploaded['id']}", headers=a_headers)
    assert got.json()["quill_content"] == "<p>edited</p>"


def test_owner_can_delete(client, uploaded, fake_s3, a_headers):
    res = client.delete(f"/api/v1/files/{uploaded['id']}", headers=a_headers)
    assert res.status_code == 200
    assert uploaded["s3_key"] not in fake_s3.objects
    assert client.get(f"/api/v1/files/{uploaded['id']}", headers=a_headers).status_code == 404


def test_other_user_sees_empty_list(client, uploaded, b_headers):
    assert client.get("/api/v1/files/", headers=b_headers).json() == []


@pytest.mark.parametrize(
    "method, path, kwargs",
    [
        ("get", "", {}),
        ("get", "/content", {}),
        ("get", "/download", {}),
        ("post", "/update-quill-content", {"data": {"quill_content": "<p>hijack</p>"}}),
        ("post", "/share", {}),
        ("delete", "", {}),
    ],
)
def test_other_user_cannot_access(client, uploaded, fake_s3, a_headers, b_headers, method, path, kwargs):
    res = getattr(client, method)(f"/api/v1/files/{uploaded['id']}{path}", headers=b_headers, **kwargs)
    assert res.status_code == 404
    # A's file is untouched
    got = client.get(f"/api/v1/files/{uploaded['id']}", headers=a_headers)
    assert got.status_code == 200
    assert got.json()["quill_content"] != "<p>hijack</p>"
    assert uploaded["s3_key"] in fake_s3.objects


def test_files_require_authentication(client, uploaded):
    assert client.get("/api/v1/files/").status_code == 401
    assert client.get(f"/api/v1/files/{uploaded['id']}").status_code == 401


def test_save_as_sent_by_editor_succeeds(client, uploaded, a_headers):
    """The editor's Save sends PUT /files/{id} with {filename, content}."""
    res = client.put(
        f"/api/v1/files/{uploaded['id']}",
        headers=a_headers,
        json={"filename": "renamed.txt", "content": "<p>ignored here</p>"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["id"] == uploaded["id"]
    assert body["filename"] == "renamed.txt"
    assert client.get(f"/api/v1/files/{uploaded['id']}", headers=a_headers).json()["filename"] == "renamed.txt"


def test_save_updates_modified_time(client, uploaded, a_headers):
    res = client.put(f"/api/v1/files/{uploaded['id']}", headers=a_headers, json={"filename": "x.txt"})
    assert res.json()["updated_at"] > uploaded["updated_at"]


def test_save_rejects_empty_filename(client, uploaded, a_headers):
    res = client.put(f"/api/v1/files/{uploaded['id']}", headers=a_headers, json={"filename": "  "})
    assert res.status_code == 422


def test_other_user_cannot_save(client, uploaded, a_headers, b_headers):
    res = client.put(f"/api/v1/files/{uploaded['id']}", headers=b_headers, json={"filename": "hijack.txt"})
    assert res.status_code == 404
    assert client.get(f"/api/v1/files/{uploaded['id']}", headers=a_headers).json()["filename"] == "notes.txt"


def test_replacing_content_updates_size(client, uploaded, fake_s3, a_headers):
    res = client.post(
        f"/api/v1/files/{uploaded['id']}/content",
        headers=a_headers,
        files={"file": ("notes.txt", b"a much longer replacement body", "text/plain")},
    )
    assert res.status_code == 200, res.text
    got = client.get(f"/api/v1/files/{uploaded['id']}", headers=a_headers).json()
    assert got["file_size"] == len(b"a much longer replacement body")
    assert fake_s3.objects[uploaded["s3_key"]] == b"a much longer replacement body"
