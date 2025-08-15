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
    uploaded = {}
    def fake_upload(image_bytes, path):
        uploaded["image_bytes"] = image_bytes
        uploaded["path"] = path
        return f"https://cdn.example/{path}"

    inserted = {}
    class FakeTable:
        def insert(self, data):
            inserted.update(data)
            class Exec:
                def execute(self_inner):
                    return None
            return Exec()

    class FakeClient:
        def table(self, name):
            inserted["table"] = name
            return FakeTable()

    monkeypatch.setattr(helpers, "get_client", lambda: FakeClient())
    monkeypatch.setattr(helpers, "upload_image", fake_upload)

    url = helpers.save_article_image(1, "foo", b"bytes")
    assert uploaded["image_bytes"] == b"bytes"
    assert uploaded["path"].startswith("1/")
    assert inserted["table"] == "article_images"
    assert inserted["article_id"] == 1
    assert inserted["diagram_type"] == "foo"
    assert inserted["image_url"] == url
    assert url.startswith("https://cdn.example/1/")
