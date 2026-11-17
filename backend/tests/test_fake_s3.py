import inspect

from app.services.s3_service import S3Service

from .conftest import FakeS3


def test_fake_matches_real_s3_service_signatures():
    for name in FakeS3.METHODS:
        real = getattr(S3Service, name)
        fake = getattr(FakeS3, name)
        assert list(inspect.signature(real).parameters) == list(inspect.signature(fake).parameters), name
