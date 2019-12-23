import pytest

# from pytest_django.live_server_helper import LiveServer
#
# import socket

from django.conf import settings
from django.test import RequestFactory

from collab_canvas.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> settings.AUTH_USER_MODEL:
    return UserFactory()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


# @pytest.fixture(scope='class')
# def test_server() -> LiveServer:
#     settings.DEBUG = True
#     address = socket.gethostbyname(socket.gethostname())
#     settings.ALLOWED_HOSTS += address
#     server = LiveServer(address)
#     yield server
#     server.stop()
