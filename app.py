import os
from flask import Flask

from api.mail import mail
from api.main_page import main_page
from api.error_handle import page_not_found
from api.simulator_api import simulator_api
from config import Config
from database.db import db
from usersettings.delete import delete
from usersettings.login import login
from usersettings.logout import logout
from usersettings.register import signup
from usersettings.validate import validate

if __name__ == "__main__":
    # for debug purpose:
    # os.environ['REDIS_SERVER'] = '172.23.0.2'
    # os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dna_sim:***REMOVED***@172.23.0.3:5432/dna_sim'
    os.environ['REDIS_SERVER'] = '172.30.0.2'
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dna_sim:***REMOVED***@172.30.0.3:5432/dna_sim'
    # ENVIRONMENT VARIABLE 'API_PORT' CAN CHANGE THE API PORT (e.g. for DOCKER)
    # app = create_app()
    app = Flask(__name__)
    app.config.from_object(Config)  # Choose from the different configs...

    db.init_app(app)
    mail.init_app(app)
    # db.init_app(app)

    # blueprint for auth routes in our app
    # from api.auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)

    app.register_blueprint(main_page)
    app.register_blueprint(login)
    app.register_blueprint(logout)
    app.register_blueprint(delete)
    app.register_blueprint(validate)
    app.register_blueprint(signup)

    app.register_blueprint(simulator_api)

    app.register_error_handler(404, page_not_found)
    # from database import db

    # db.init_app(app)

    # db.create_all(app=create_app())
    port = int(os.environ.get("API_PORT", 5000))
    app.run(host=os.environ.get("API_IP", "0.0.0.0"), port=port)
