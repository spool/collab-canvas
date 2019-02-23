"""
UX testing with Channels underneath.

Amalgamation of the Channels tutorial: https://channels.readthedocs.io/en/latest/tutorial

and

https://medium.com/zeitcode/a-simple-recipe-for-django-development-in-docker-bonus-testing-with-selenium-6a038ec19ba5

"""
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from channels.testing.live import ChannelsLiveServerTestCase
from django.test import tag

from .utils import CellFactory, UserFactory
from .test_views import BaseDynamicCanvasTest


@tag('selenium')
class BaseUXTest(ChannelsLiveServerTestCase, BaseDynamicCanvasTest):

    serve_static = True

    """Base class to test for Chrome and Firefox UX."""

    @classmethod
    def setUpClass(cls):
        """Setup to ensure selenium is close to normal UX."""
        super().setUpClass()
        cls.chrome = webdriver.Remote(
            command_executor='http://hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
        )
        cls.chrome.implicitly_wait(10)
        # cls.firefox = webdriver.Remote(
        #     command_executor='http://129.0.0.1:4444/wd/hub',
        #     desired_capabilities=DesiredCapabilities.FIREFOX
        # )
        # cls.firefox.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        """Ensure selenium shuts down with tests."""
        cls.chrome.quit()
        super().tearDownClass()

    def setUp(self):
        """Ensure cell and user are setup and assigned to test."""
        super().setUp()
        self.user = UserFactory()
        self.cell = CellFactory(canvas=self.canvas, artist=self.user)

    def _url_prefix(self, url: str = None) -> str:
        """Shortcut to prefix str with live url."""
        return self.live_server_url + url

    def test_canvas_render(self):
        """Test basic canvas is rendered in template."""
        self.chrome.get(self._url_prefix('/home'))
        self.chrome.get(self._url_prefix(self.cell.get_absolute_url()))
