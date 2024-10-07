from flask import Flask, render_template
import requests
import secret

app = Flask(__name__)

CLIENT_ID = secret.CLIENT_ID
CLIENT_SECRET = secret.CLIENT_SECRET

def get_oauth_token():
    # The URL for the OAuth token
    token_url = "https://www.warcraftlogs.com/oauth/token"
    print(token_url)
    
    # Request payload
    data = {
        'grant_type': 'client_credentials'
    }

    print(data)
    
    # Make the POST request with Basic Authentication
    response = requests.post(token_url, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response to get the token
        token_info = response.json()
        return token_info['access_token']
    else:
        # Handle the error
        print(f"Failed to get token: {response.status_code}, {response.text}")
        return None
    



@app.route('/')
def home():

    oauth_token = get_oauth_token()

    if oauth_token:
        print(f"Received OAuth token: {oauth_token}")
    else:
        print("Failed to retrieve OAuth token.")

    return render_template('home.html')



if __name__ == "__main__":
    app.run(debug=True)
