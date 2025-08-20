import random
from locust import HttpUser, task, between

class RegistrationUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    @task
    def register_user_flow(self):
        # Use a unique mobile number for each simulated user
        mobile_number = f"+8801{random.randint(100000000, 999999999)}"
        password = "testPassword123"

        # Step 1: Request OTP
        self.client.post(
            "/api/v1/auth/register/request-otp",
            json={"mobile_number": mobile_number, "password": password}
        )
        
        # NOTE: In a real test, we would need a way to get the OTP.
        # Since our mock OTP is only printed to the log, we can't complete the flow.
        # For this test, we will only simulate the first step (requesting the OTP),
        # as this is the most public and vulnerable endpoint to a flood of requests.