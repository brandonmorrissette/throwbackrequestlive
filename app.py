from flask import Flask, render_template
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

@app.route('/')
def home():
    events = get_events()
    return render_template('home.html', events=events)

@app.route("/tip")
def tip():
    return render_template("tip.html")

@app.route("/book")
def book():
    return render_template("book.html")

@app.route("/survey")
def survey():
    return render_template("survey.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
