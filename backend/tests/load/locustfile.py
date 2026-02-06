"""
Load Tests with Locust

Locust load testing scenarios for MCP server and chat endpoint.
"""

from locust import HttpUser, task, between
import json


class ChatUser(HttpUser):
    """
    Simulated user for load testing chat endpoint.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """
        Setup: Login and get JWT token before starting tasks.
        """
        # Signup
        signup_response = self.client.post("/api/auth/signup", json={
            "email": f"loadtest_{self.environment.runner.user_count}@example.com",
            "password": "password123",
            "name": f"Load Test User {self.environment.runner.user_count}"
        })

        if signup_response.status_code == 201:
            # Login
            login_response = self.client.post("/api/auth/signin", json={
                "email": f"loadtest_{self.environment.runner.user_count}@example.com",
                "password": "password123"
            })

            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data["access_token"]
                self.user_id = data["user"]["id"]
            else:
                self.token = None
                self.user_id = None
        else:
            # User might already exist, try login
            login_response = self.client.post("/api/auth/signin", json={
                "email": f"loadtest_{self.environment.runner.user_count}@example.com",
                "password": "password123"
            })

            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data["access_token"]
                self.user_id = data["user"]["id"]
            else:
                self.token = None
                self.user_id = None

    @task(3)
    def chat_create_task(self):
        """
        Task: Create a task via chat endpoint (weight: 3)
        """
        if not self.token:
            return

        self.client.post(
            f"/api/{self.user_id}/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"message": "Add a task to test load"}
        )

    @task(5)
    def chat_list_tasks(self):
        """
        Task: List tasks via chat endpoint (weight: 5)
        """
        if not self.token:
            return

        self.client.post(
            f"/api/{self.user_id}/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"message": "Show me my tasks"}
        )

    @task(2)
    def chat_mark_complete(self):
        """
        Task: Mark task complete via chat endpoint (weight: 2)
        """
        if not self.token:
            return

        self.client.post(
            f"/api/{self.user_id}/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"message": "Mark my first task as done"}
        )

    @task(1)
    def chat_delete_task(self):
        """
        Task: Delete task via chat endpoint (weight: 1)
        """
        if not self.token:
            return

        self.client.post(
            f"/api/{self.user_id}/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"message": "Delete my first task"}
        )


# Run with: locust -f locustfile.py --host=http://localhost:8000
# Then open http://localhost:8089 to configure and start load test
