from locust import HttpUser, task, between
import uuid
import json

class FlashSaleTrafficSimulator(HttpUser):
    # Simulate a rapid user interaction wait time (0.1 to 0.5 seconds between clicks)
    wait_time = between(0.1, 0.5)

    @task
    def purchase_attempt(self):
        payload = {
            "user_id": f"locust_user_{uuid.uuid4().hex[:6]}",
            "product_id": "shoe_101"
        }
        headers = {"Content-Type": "application/json"}
        
        # We tell Locust to expect 423 status codes without marking them as system failures
        with self.client.post("/orders", data=json.dumps(payload), headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 423:
                response.success()  # Business logic 'sold out' is an expected successful rejection
            else:
                response.failure(f"System degraded with status code: {response.status_code}")