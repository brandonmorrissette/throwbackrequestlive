from flask import Flask, render_template, redirect, request, url_for
import csv
from datetime import datetime

app = Flask(__name__)

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

@app.route('/')
def home():
    return render_template('home.html', events=get_events())

@app.route("/tip")
def tip():
    return render_template("tip.html")

@app.route("/book")
def book():
    return render_template("book.html")

@app.route("/survey")
def survey():
    return render_template("survey.html", songs=get_songs())

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
