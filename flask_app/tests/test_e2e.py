import unittest
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from app import create_app



class TestE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Define DB path
        cls.db_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'e2e_test.db'
        )

        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

        os.environ['DATABASE_URL'] = f'sqlite:///{cls.db_path}'

        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False

        # Start Flask Server
        cls.port = 5002
        cls.server_thread = threading.Thread(
            target=cls.app.run,
            kwargs={'port': cls.port, 'use_reloader': False}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()

        time.sleep(1)

        # Setup Selenium WebDriver (Headless)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        # Clean up DB
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self):
        self.base_url = f"http://127.0.0.1:{self.port}"

    def test_browser_flow(self):
        driver = self.driver

        # 1. Register
        driver.get(f"{self.base_url}/register")
        driver.find_element(By.NAME, "username").send_keys("e2e_user")
        driver.find_element(By.NAME, "password").send_keys("password")
        driver.find_element(By.NAME, "confirm").send_keys("password")
        driver.find_element(By.TAG_NAME, "button").click()

        try:
            self.assertIn("/login", driver.current_url)
        except AssertionError:
            print("Registration failed. Current URL:", driver.current_url)
            print("Page Source:", driver.page_source)
            raise

        # 2. Login
        driver.find_element(By.NAME, "username").send_keys("e2e_user")
        driver.find_element(By.NAME, "password").send_keys("password")
        driver.find_element(By.TAG_NAME, "button").click()

        self.assertEqual(
            driver.current_url.rstrip('/'), self.base_url.rstrip('/')
        )
        self.assertIn("Your Tasks", driver.page_source)

        # 3. Create Task
        driver.find_element(By.LINK_TEXT, "Create your first task").click()

        driver.find_element(By.NAME, "title").send_keys("Selenium Task")
        driver.find_element(By.NAME, "description").send_keys(
            "Automated description"
        )

        date_input = driver.find_element(By.NAME, "due_date")
        driver.execute_script("arguments[0].value = '2025-12-31';", date_input)

        driver.find_element(By.TAG_NAME, "button").click()

        self.assertIn("Selenium Task", driver.page_source)

        # 4. Toggle Task
        complete_btn = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Complete')]"
        )
        complete_btn.click()
        time.sleep(0.5)
        self.assertIn("Reopen", driver.page_source)

        # 5. Delete Task
        delete_btn = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Delete')]"
        )
        delete_btn.click()

        alert = driver.switch_to.alert
        alert.accept()

        time.sleep(0.5)
        self.assertNotIn("Selenium Task", driver.page_source)

if __name__ == "__main__":
    unittest.main()
