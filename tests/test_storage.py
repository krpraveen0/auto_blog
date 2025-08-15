from db import storage, helpers


def test_upload_image(monkeypatch):
    class FakeBucket:
        def __init__(self):
            self.path = None
            self.data = None
        def upload(self, path, data):
            self.path = path
            self.data = data
        def get_public_url(self, path):
            return f"https://cdn.example/{path}"

    class FakeStorage:
        def __init__(self):
            self.bucket = FakeBucket()
        def from_(self, bucket_name):
            assert bucket_name == storage.BUCKET_NAME
            return self.bucket

    class FakeClient:
        def __init__(self):
            self.storage = FakeStorage()

    fake_client = FakeClient()
    monkeypatch.setattr(storage, "get_client", lambda: fake_client)

    url = storage.upload_image(b"img", "1/file.png")
    assert fake_client.storage.bucket.path == "1/file.png"
    assert fake_client.storage.bucket.data == b"img"
    assert url == "https://cdn.example/1/file.png"


def test_save_article_image(monkeypatch):
    uploaded = []

    def fake_upload(image_bytes, path):
        uploaded.append({"image_bytes": image_bytes, "path": path})
        return f"https://cdn.example/{path}"

    inserted_rows = []

    class FakeTable:
        def insert(self, data):
            inserted_rows.append(data)
            class Exec:
                def execute(self_inner):
                    return None
            return Exec()

    class FakeClient:
        def table(self, name):
            assert name == "article_images"
            return FakeTable()

    monkeypatch.setattr(helpers, "get_client", lambda: FakeClient())
    monkeypatch.setattr(helpers, "upload_image", fake_upload)

    url1 = helpers.save_article_image(1, "foo", b"bytes1")
    url2 = helpers.save_article_image(1, "bar", b"bytes2")

    assert uploaded[0]["image_bytes"] == b"bytes1"
    assert uploaded[1]["image_bytes"] == b"bytes2"
    assert uploaded[0]["path"].startswith("1/")
    assert uploaded[1]["path"].startswith("1/")
    assert inserted_rows[0]["diagram_type"] == "foo"
    assert inserted_rows[1]["diagram_type"] == "bar"
    assert inserted_rows[0]["image_url"] == url1
    assert inserted_rows[1]["image_url"] == url2
    assert url1.startswith("https://cdn.example/1/")
    assert url2.startswith("https://cdn.example/1/")
    assert all(row["article_id"] == 1 for row in inserted_rows)
