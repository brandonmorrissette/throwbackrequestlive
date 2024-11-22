from flask import Blueprint, render_template, redirect, request, url_for, jsonify, current_app as app
from backend.webapp.services import get_events, get_songs, record_vote_logic, admin_login_logic

bp = Blueprint('routes', __name__)

# Routes
@bp.route('/')
def home():
    return render_template('home.html', events=get_events())

@bp.route("/tip")
def tip():
    return render_template("tip.html")

@bp.route("/book")
def book():
    return render_template("book.html")

@bp.route("/vote")
def vote():
    return render_template("vote.html", songs=get_songs())

@bp.route('/record-vote', methods=['POST'])
def record_vote():
    data = request.get_json()
    record_vote_logic(data)
    return redirect(url_for('routes.thank_you', song_name=data.get('song')))

@bp.route('/thank-you')
def thank_you():
    song_name = request.args.get('song_name', 'your song')
    return render_template('thank_you.html', song_name=song_name, events=get_events())

@bp.route('/admin')
def admin():
    return render_template('admin.html')

@bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    return jsonify(admin_login_logic(data))