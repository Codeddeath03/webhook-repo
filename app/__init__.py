from flask import Flask,render_template
from app.extensions import mongo 
from app.webhook.routes import webhook
from app.ui.routes import ui

# Creating our flask app
def create_app():

    app = Flask(__name__)

    app.config["MONGO_URI"] = "mongodb://localhost:27017/database"
    mongo.init_app(app)
    
    # registering all the blueprints
    app.register_blueprint(webhook)
    app.register_blueprint(ui)

    return app
