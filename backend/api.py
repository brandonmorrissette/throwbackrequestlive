from flask import Blueprint, current_app as app, jsonify, request, redirect
import boto3
from botocore.exceptions import ClientError
import csv
from datetime import datetime
import os

bp = Blueprint('routes', __name__)

@app.route('/vote')
def render_vote():
    return app.send_static_file('index.html')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def render_main(path):
    return app.send_static_file('index.html')


def login(data):
    username = data.get('username')
    password = data.get('password')
    response_dict = {'success': False}

    try:
        response = boto3.client('cognito-idp', region_name=app.config['COGNITO_REGION']).initiate_auth(
            ClientId=app.config['COGNITO_APP_CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        response_dict.update({'response': response})
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 and 'AuthenticationResult' in response:
            response_dict.update({
            'success': True,
            'access_token': response['AuthenticationResult']['AccessToken'],
            'id_token': response['AuthenticationResult']['IdToken'],
            'refresh_token': response['AuthenticationResult'].get('RefreshToken')
            })
        else:
            app.logger.error(f"Authentication failed or AuthenticationResult not in response: {response}")
        
        return response_dict
        
    except ClientError as e:
        app.logger.error(f"Login failed: {e}")
        response_dict.update({'error': str(e)})
        return response_dict
    
@app.route('/api/vote', methods=['POST'])
def handle_vote():
    vote_data = request.get_json()
    print("Vote data received:", vote_data)
    song_name = vote_data.get('song')
    return redirect(f"/?song={song_name}")

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
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'songs.csv')
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