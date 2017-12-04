from django.test import TestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from edc_list_data.site_list_data import site_list_data

import .listboard_page


class ListboardSearch(TestCase):
    """A sample test class to show how page object works"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        site_list_data.autodiscover()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        import_randomization_list()
        url_names = (self.extra_url_names
                     + list(settings.DASHBOARD_URL_NAMES.values())
                     + list(settings.LAB_DASHBOARD_URL_NAMES.values())
                     + list(dashboard_urls.values()))
        self.url_names = list(set(url_names))
        super().setUp()

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get("http://www.python.org")

    def test_search_in_python_org(self):
        """
        Tests python.org search feature. Searches for the word "pycon" then verified that some results show up.
        Note that it does not look for any particular text in search results page. This test verifies that
        the results were not empty.
        """

        # Load the main page. In this case the home page of Python.org.
        main_page = page.MainPage(self.driver)
        # Checks if the word "Python" is in title
        assert main_page.is_title_matches(), "python.org title doesn't match."
        # Sets the text of search textbox to "pycon"
        main_page.search_text_element = "pycon"
        main_page.click_go_button()
        search_results_page = page.SearchResultsPage(self.driver)
        # Verifies that the results page is not empty
        assert search_results_page.is_results_found(), "No results found."

    def tearDown(self):
        self.driver.close()
