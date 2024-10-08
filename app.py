from flask import Flask, jsonify, render_template
import requests
import secret

app = Flask(__name__)

CLIENT_ID = secret.CLIENT_ID
CLIENT_SECRET = secret.CLIENT_SECRET


# API route to generate token or serve data
@app.route('/get_token', methods=['GET'])
def get_token():
    token = get_oauth_token()
    return jsonify({'token': token})


@app.route('/')
def home():
    access_token = get_oauth_token()

    if access_token:
        parse1 = get_boss_parses(access_token)

    return render_template('index.html')


def get_oauth_token():
    # The URL for the OAuth token
    token_url = "https://www.warcraftlogs.com/oauth/token"

    # Request payload
    data = {
        'grant_type': 'client_credentials'
    }

    # Make the POST request with Basic Authentication
    response = requests.post(token_url, data=data,
                             auth=(CLIENT_ID, CLIENT_SECRET))

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response to get the token
        token_info = response.json()
        return token_info['access_token']
    else:
        # Handle the error
        print(f"Failed to get token: {response.status_code}, {response.text}")
        return None


def get_character_data(access_token, character_name, server_slug, server_region, encounter_ids):
    parses = {}

    for encounter_id in encounter_ids:
        query = f"""
        {{
          characterData {{
            character(name: "{character_name}", serverSlug: "{server_slug}", serverRegion: "{server_region}") {{
              canonicalID
              classID
              guildRank
              id
              level
              name
              encounterRankings(
                encounterID: {encounter_id}
                difficulty: 4
              )
            }}
          }}
        }}
        """

        url = "https://www.warcraftlogs.com/api/v2/client"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Send the POST request with the GraphQL query
        response = requests.post(url, json={'query': query}, headers=headers)

        if response.status_code == 200:
            character_data = response.json()
            # Extract and process the JSON encounter rankings data
            try:
                rankings_data = character_data['data']['characterData']['character']['encounterRankings']

                # Process the JSON response here to get rankPercent
                # Assuming `rankings_data` is now a JSON object with the ranking info
                if rankings_data:
                    rank_percent = rankings_data['ranks'][0]['rankPercent']
                    parses[encounter_id] = int(rank_percent)
                else:
                    print(
                        f"No rankings data available for encounter {encounter_id}")
            except (KeyError, IndexError):
                print(
                    f"Could not retrieve rank percent for encounter {encounter_id}")
        else:
            print(
                f"Failed to get data for encounter {encounter_id}: {response.status_code}, {response.text}")

    return parses


def get_boss_parses(access_token):
    if access_token:
        character_name = 'Vannskii'         # Replace with your character name
        # Replace with your server slug (lowercase)
        server_slug = 'stormrage'
        server_region = 'us'                 # Replace with your server region

        # List of encounter IDs for the bosses you're tracking
        encounter_ids = [2902, 2917, 2898, 2918, 2919, 2920, 2921, 2922]

        # Fetch parses for all the encounters
        character_parses = get_character_data(
            access_token, character_name, server_slug, server_region, encounter_ids)

        # Print the parse results for each boss
        for encounter_id, rank_percent in character_parses.items():
            print(
                f"Boss with encounter ID {encounter_id}: Rank Percent = {rank_percent}")


if __name__ == "__main__":
    app.run(debug=True)
