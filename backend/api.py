from flask import Blueprint, current_app as app, jsonify
import boto3
from botocore.exceptions import ClientError
import csv
from datetime import datetime
import os

bp = Blueprint('routes', __name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    app.logger.debug(f"Request received for path: {path}")
    
    if not path or not os.path.exists(os.path.join(app.static_folder, path)):
        app.logger.debug("Serving React index.html")
        return app.send_static_file('index.html')


    app.logger.debug(f"Serving static file: {path}")
    return app.send_static_file(path)


def record_vote_logic(data):
    song_name = data.get('song')

def admin_login_logic(data):
    username = data.get('username')
    password = data.get('password')

    try:
        response = boto3.client('cognito-idp', region_name=app.config['COGNITO_REGION']).initiate_auth(
            ClientId=app.config['COGNITO_APP_CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 and 'AuthenticationResult' in response:
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            refresh_token = response['AuthenticationResult'].get('RefreshToken')

            return {'success': True, 'access_token': access_token, 'id_token': id_token, 'refresh_token': refresh_token}
        else:
            app.logger.error(f"Authentication failed or AuthenticationResult not in response: {response}")
            return {'success': False, 'error': "Authentication failed. Please try again.", 'response': response}
    
    except ClientError as e:
        app.logger.error(f"Login failed: {e}")
        return {'success': False, 'error': "Invalid credentials. Please try again.", 'response': str(e)}

@bp.route('/api/shows', methods=['GET'])
def get_shows():
    shows = []
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'shows.csv')
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            show_datetime = datetime.strptime(f"{row['date']} {row['time']}", '%m-%d-%Y %I:%M %p')
            if show_datetime >= datetime.now():
                shows.append({
                    'name': row['name'],
                    'date': row['date'],
                    'time': row['time'],
                    'venue': row['venue'],
                    'street': row['street'],
                    'city': row['city'],
                    'state': row['state']
                })
    return jsonify(shows)

@bp.route('/api/songs', methods=['GET'])
def get_songs():
    songs = []
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'songs.csv')
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            songs.append({
                'band': row['Band'],
                'song_name': row['Song Name'],
                'total_votes': int(row['Total Votes']),
                'votes_per_show': int(row['Votes Per Show'])
            })
    return jsonify(songs)