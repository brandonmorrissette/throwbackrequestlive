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

@app.route('/login')
def render_login():
    return app.send_static_file('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400

    try:
        client = boto3.client('cognito-idp', region_name=os.getenv('COGNITO_REGION'))
        response = client.initiate_auth(
            ClientId=os.getenv('COGNITO_APP_CLIENT_ID'),
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        if 'AuthenticationResult' in response:
            auth_result = response['AuthenticationResult']
            return jsonify({
                'success': True,
                'access_token': auth_result['AccessToken'],
                'id_token': auth_result['IdToken'],
                'refresh_token': auth_result.get('RefreshToken')
            }), 200
        else:
            return jsonify({'success': False, 'error': f'Authentication failed : {response}'}), 401

    except ClientError as e:
        error_message = e.response['Error']['Message']
        app.logger.error(f"Cognito login failed: {error_message}")
        return jsonify({'success': False, 'error': error_message}), 500

    
@app.route('/api/vote', methods=['POST'])
def post_vote():
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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def render_main(path):
    return app.send_static_file('index.html')