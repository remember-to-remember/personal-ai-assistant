import requests
import streamlit as st
from streamlit_auth0_component import login_button

clientId = "R577GEvCtUPJ24A7sqpUpLm3FU0ov6XF"
domain = "remember-to-remember.au.auth0.com"

user_info = login_button(clientId, domain=domain, audience="personal-ai-assistant")
st.write(user_info)

if user_info:
    st.title("Secure API Client")

    api_url = st.text_input("API URL", value="https://api.remember2.co:8001/chat")

    def call_api(api_url, token):
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(api_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            return {"error": str(err)}

    if st.button("Call API"):
        if not api_url or not user_info:
            st.error("API URL and Bearer Token are required")
        else:
            token = user_info.get("token", {})
            email = user_info.get("email", "")
            result = call_api(api_url, f"{token}:{email}")
            st.write(result)
