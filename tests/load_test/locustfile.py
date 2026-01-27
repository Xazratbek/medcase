import random
import string
import json
from locust import HttpUser, task, between, events
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedCaseUser(HttpUser):
    wait_time = between(1, 5)  # Simulate user think time between 1 and 5 seconds

    def on_start(self):
        """
        Executed when a user starts. We register a new user or login if already exists.
        Since we need unique users for realistic load, we'll try to register a random user.
        """
        self.email = f"loadtest_{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"
        self.password = "Password123" # Stronger password
        self.token = None

        # 1. Register
        reg_payload = {
            "ism": "LoadTester",
            "familiya": "User",
            "email": self.email,
            "parol": self.password,
            "parol_tasdiqlash": self.password,
            "telefon": f"+998{random.randint(100000000, 999999999)}",
            "foydalanuvchi_nomi": self.email.split("@")[0]
        }

        with self.client.post("/api/v1/autentifikatsiya/royxatdan-otish", json=reg_payload, catch_response=True) as response:
            if response.status_code == 200 or response.status_code == 201:
                # Registration successful
                pass
            elif response.status_code == 400 and "mavjud" in response.text:
                pass
            else:
                logger.error(f"Registration failed: {response.text}")

        # 2. Login
        login_payload = {
            "email_yoki_nom": self.email,  # Schema uses email_yoki_nom
            "parol": self.password
        }

        with self.client.post("/api/v1/autentifikatsiya/kirish", json=login_payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("kirish_tokeni")
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            else:
                logger.error(f"Login failed: {response.text}")
                self.token = None

    @task(3)
    def get_dashboard(self):
        if not self.token:
            return

        with self.client.get("/api/v1/rivojlanish/dashboard", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Dashboard failed with {response.status_code}: {response.text}")

    @task(2)
    def get_profile(self):
        if not self.token:
            return

        with self.client.get("/api/v1/autentifikatsiya/men", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Profile failed with {response.status_code}: {response.text}")

    @task(1)
    def get_categories(self):
        if not self.token:
            return

        # Checking 'kategoriya' endpoint based on file list
        # Assuming '/api/v1/kategoriya/asosiy' exists based on files
        with self.client.get("/api/v1/kategoriya/asosiy", catch_response=True) as response:
             if response.status_code != 200:
                 pass

    def on_stop(self):
        pass
