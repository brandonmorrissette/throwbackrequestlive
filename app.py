from flask import Flask, render_template, redirect
import csv

app = Flask(__name__)

@app.route('/')
def home():
    events = []
    with open('data/events.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            events.append({
                'name': row['name'], 
                'date': row['date'],        
                'venue': row['venue'],  
                'address': row['address']     
            })
    return render_template('home.html', events=events)
    
@app.route("/tip")
def tip():
    return redirect("https://tiptopjar.com/throwbackrequestlive", code=302)
    
@app.route("/contact")
def contact():
    return render_template("contact.html")
    
@app.route("/survey")
def survey():
    return render_template("survey.html")

@app.route("/socials")
def socials():
    return render_template("socials.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
