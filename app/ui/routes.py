from flask import Blueprint, render_template

ui = Blueprint('ui', __name__)

@ui.route('/ui')
def dashboard():
    return render_template("dasboard.html")
