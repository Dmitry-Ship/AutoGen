from typing import Annotated, Dict
import requests
import time

class ArtGeneration:
    def __init__(self, email: str, password: str, model_id=138):
        self.url_base = 'https://artgeneration.me/api'
        self.email = email
        self.password = password
        self.base_data = {
            "model_id": model_id,
            "width": 1280,
            "height": 768,
            "is_private": True,
            "num_inference_steps": 31,
            "guidance_scale": 5,
            "scheduler_id": "d5a6df48-3f33-49e3-8936-a89c3146167b",
            "self_attention": False,
            "clip_skip": 1,
            "highres_fix": False,
            "sharpness": 2,
            "samples": 1
        } 

        self.user_id = None
        result = self.authenticate()
    
    def authenticate(self):
        auth_url = f"{self.url_base}/auth/email/auth"
        auth_data = {
            "email": self.email,
            "password": self.password
        }
        response = requests.post(auth_url, json=auth_data).json()
        
        if "data" in response and "user" in response["data"]:
            self.base_data["token"] = response["data"]["user"]["token"]
            self.user_id = response["data"]["user"]["id"]
            return True, "Authentication Successful"
        else:
            return False, "Authentication Failed"
    def send_request(self, prompt):
        data = self.base_data.copy()
        data["prompt"] = prompt
        response = requests.post(f"{self.url_base}/v1/image/init", json=data)

        return response.json()

    def fetch_generation_list(self):
        params = {
            'user_id': self.user_id,
            'subscription_type': 'premium',
        }
        response = requests.get(f"{self.url_base}/v1/image/fetch/", params=params)
        return response.json()

    def generate_image(self, prompt: Annotated[str, "Prompt"]) -> Annotated[Dict[str, any], "Image info"]:
        request_response = self.send_request(prompt)
        generation_id = request_response["data"]["generation_id"]

        start_time = time.time()
        timeout = 100  # seconds

        time.sleep(30) 
        while time.time() - start_time < timeout:
            time.sleep(5)  # Wait for 5 seconds before checking again
            generation_list_response = self.fetch_generation_list()
            generation_list = generation_list_response["data"]["generation_list"]

            for generation in generation_list:
                if generation["id"] == generation_id and "image_list" in generation:
                    if len(generation["image_list"]) > 0:
                        return generation["image_list"][0]['link']
        return "Error: Image generation timed out or not found."

