from flask import Flask, render_template, redirect, request, url_for, jsonify
import csv
from datetime import datetime
import os
import boto3
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from botocore.exceptions import ClientError

import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.DEBUG)

app.config['COGNITO_REGION'] = os.getenv('AWS_REGION', 'us-east-1')  
app.config['COGNITO_USER_POOL_ID'] = os.getenv('COGNITO_USER_POOL_ID', '<your-user-pool-id>')
app.config['COGNITO_APP_CLIENT_ID'] = os.getenv('COGNITO_APP_CLIENT_ID', '<your-app-client-id>')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key') 

jwt = JWTManager(app)  

cognito = boto3.client('cognito-idp', region_name=app.config['COGNITO_REGION'])

def get_events():
    events = []
    with open('data/events.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            event_datetime = datetime.strptime(f"{row['date']} {row['time']}", '%m-%d-%Y %I:%M %p')
            if event_datetime >= datetime.now():
                events.append({
                    'name': row['name'],
                    'date': row['date'],
                    'time': row['time'],
                    'venue': row['venue'],
                    'street': row['street'],
                    'city': row['city'],
                    'state': row['state']
                })
    return events

def get_songs():
    songs = []
    with open('data/songs.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            songs.append({
                'band': row['Band'],
                'song_name': row['Song Name'],
                'total_votes': int(row['Total Votes']),
                'votes_per_show': int(row['Votes Per Show'])
            })
    return songs

# Routes
@app.route('/')
def home():
    return render_template('home.html', events=get_events())

@app.route("/tip")
def tip():
    return render_template("tip.html")

@app.route("/book")
def book():
    return render_template("book.html")

@app.route("/vote")
def vote():
    return render_template("vote.html", songs=get_songs())

@app.route('/record-vote', methods=['POST'])
def record_vote():
    data = request.get_json()
    song_name = data.get('song')

    # Record the vote logic here (e.g., save to database)

    # Redirect to the thank-you page with the song name
    return redirect(url_for('thank_you', song_name=song_name))

@app.route('/thank-you')
def thank_you():
    song_name = request.args.get('song_name', 'your song')
    return render_template('thank_you.html', song_name=song_name, events=get_events())

@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form 
    username = data.get('username')
    password = data.get('password')

    try:
        response = cognito.initiate_auth(
            ClientId=app.config['COGNITO_APP_CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        id_token = response['AuthenticationResult']['IdToken']
        access_token = create_access_token(identity=username)

        return redirect(url_for('admin', token=access_token))

    except ClientError as e:
        app.logger.error(f"Login failed: {e}")
        return redirect(url_for('admin', error="Invalid username or password"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
