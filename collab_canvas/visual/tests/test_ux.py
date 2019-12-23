"""
UX testing with Channels underneath.

Amalgamation of the Channels tutorial: https://channels.readthedocs.io/en/latest/tutorial

and

https://medium.com/zeitcode/a-simple-recipe-for-django-development-in-docker-bonus-testing-with-selenium-6a038ec19ba5

"""
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from typing import Optional
import socket

# import pytest

from channels.testing.live import ChannelsLiveServerTestCase

# from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.test import tag
# from django.test import tag, override_settings

from .utils import CellFactory, TEST_USER_PASSWORD  # UserFactory
from .test_views import BaseDynamicCanvasTest


@tag('selenium')
class CanvasUXTest(ChannelsLiveServerTestCase, BaseDynamicCanvasTest):

    # serve_static = True
    # host = 'django'  # Docker django host name

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
        # cls._pytest_live_server()

        # cls.firefox = webdriver.Remote(
        #     command_executor='http://129.0.0.1:4444/wd/hub',
        #     desired_capabilities=DesiredCapabilities.FIREFOX
        # )
        # cls.firefox.implicitly_wait(10)

    def _pre_setup(self):
        # from pytest_django.live_server_helper import LiveServer
        # settings.DEBUG = True
        address = socket.gethostbyname(socket.gethostname())
        self.host = address
        # self.server = LiveServer(address)
        # settings.ALLOWED_HOSTS += [address]
        # modify_settings()
        super()._pre_setup()

    @classmethod
    def tearDownClass(cls):
        """Ensure selenium shuts down with tests."""
        cls.chrome.quit()
        # settings.DEBUG = False
        super().tearDownClass()

    def tearDown(self):
        self._close_all_new_windows()

    # @classmethod
    # def _pytest_live_server(self):
    #     """Alter live server to work in docker."""
    #     import socket
    #     from pytest_django.live_server_helper import LiveServer
    #     address = socket.gethostbyname(socket.gethostname())
    #     self.server = LiveServer(address)
    #     settings.ALLOWED_HOSTS += [address]
    #     settings.DEBUG = True

    def _url_prefix(self, url: str = '') -> str:
        """Shortcut to prefix str with live url."""
        # return self.server.url + url
        return self.live_server_url + url

    def _open_new_window(self):
        self.chrome.execute_script('window.open("about:blank", "_blank");')
        # self.chrome.switch_to_window(self.chrome.window_handles[-1])

    def _switch_to_window(self, window_index: int):
        self.chrome.switch_to.window(self.chrome.window_handles[window_index])

    def _close_all_new_windows(self):
        while len(self.chrome.window_handles) > 1:
            self.chrome.switch_to.window(self.chrome.window_handles[-1])
            self.chrome.execute_script('window.close();')
        if len(self.chrome.window_handles) == 1:
            self.chrome.switch_to.window(self.chrome.window_handles[0])

    def _new_cell(self, cell_number: Optional[int] = None, **kwargs):
        cell = CellFactory(canvas=self.canvas, **kwargs)
        setattr(self, f'cell{cell_number}', cell)
        setattr(self, f'user{cell_number}', cell.artist)
        return cell, cell.artist

    def _login(self, user: settings.AUTH_USER_MODEL,
               password: Optional[str] = TEST_USER_PASSWORD,
               url: str = '/accounts/login/'):
        """Create a chrome window for a specific cell with cell owner logged in."""
        # cell = CellFactory(canvas=self.canvas, x_position=x_position,
        #                    y_position=y_position)
        self.chrome.get(self._url_prefix(url))
        print(self.chrome.find_elements_by_class_name("login"))
        username_input = self.chrome.find_element_by_id("id_login")
        username_input.send_keys(user.username)
        password_input = self.chrome.find_element_by_id("id_password")
        password_input.send_keys(password)
        # self.chrome.find_element_by_xpath('//input[@value="Sign in"]').click()
        sign_in_button = self.chrome.find_element_by_xpath(
                '//button[contains(text(), "Sign In")]')

        breakpoint()

        sign_in_button.click()

    def _new_cell_window(self, cell_number: int = 0, new_window: bool = False,
                         **kwargs):
        if new_window:
            self._open_new_window()
        cell, artist = self._new_cell(cell_number, **kwargs)
        self._login(artist)

        # previously commented out
        # self.client.login(username=cell.artist, password=TEST_USER_PASSWORD)
        # cookie = self.client.cookies['sessionid']
        # self.chrome.get(self._url_prefix(cell.get_absolute_url()))
        # self.chrome.add_cookie({'name': 'sessionid', 'value': cookie.value,
        #                         'secure': False, 'path': '/'})
        # self.chrome.refresh()
        # End commented section

    def test_selenium(self):
        """Ensure Selenium is working correctly."""
        self.chrome.get(self.live_server_url)
        self.assertEqual(self.chrome.title, 'Collab Canvas')

    def test_canvas_render(self):
        """Test basic canvas is rendered in template."""

        self._new_cell_window(0, x_position=0, y_position=0)
        # self._new_cell_window(1, new_window=True, x_position=-1, y_position=0)
        # self._switch_to_window(0)
        self.assertEqual(self.chrome.current_url,
                         self._url_prefix(self.cell0.get_absolute_url()))
