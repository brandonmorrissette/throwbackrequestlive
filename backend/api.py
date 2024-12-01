import csv
import logging
import os
from datetime import datetime

from flask import Blueprint
from flask import current_app as app
from flask import jsonify, redirect, request
from service.auth_service import AuthService

bp = Blueprint('routes', __name__)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

auth_service = AuthService()

@app.route('/vote')
def render_vote():
    return app.send_static_file('index.html')

@app.route('/admin')
def render_admin():
    return app.send_static_file('index.html')

@app.route('/login')
def render_login():
    return app.send_static_file('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    session = data.get('session')
    password_reset = data.get('password_reset')

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400

    try:
        if password_reset:
            response = auth_service.reset_password(username, password, session)
        else:
            response = auth_service.authenticate_user(username, password)

        return jsonify({
            'success': True,
            'token': response['token'],
            'user_groups': response['user_groups']
        }), 200

    except Exception as e:
        app.logger.error(f"Error during Cognito authentication: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



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