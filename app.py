import os
from flask import Flask

from api.mail import mail
from api.main_page import main_page
from api.error_handle import page_not_found
from api.simulator_api import simulator_api
from config import Config
from database.db import db
from database.models import User
from usersettings.reset_password import reset
from usersettings.delete import delete
from usersettings.login import login
from usersettings.logout import logout
from usersettings.register import signup
from usersettings.validate import validate


def main(cfg=Config):
    app = Flask(__name__)
    app.config.from_object(cfg)  # Choose from the different configs...

    db.init_app(app)
    mail.init_app(app)

    app.register_blueprint(main_page)
    app.register_blueprint(login)
    app.register_blueprint(logout)
    app.register_blueprint(delete)
    app.register_blueprint(validate)
    app.register_blueprint(signup)
    app.register_blueprint(reset)

    app.register_blueprint(simulator_api)
    app.register_error_handler(404, page_not_found)

    @app.context_processor
    def utility_processor():
        def is_user_admin(user_id):
            try:
                user = User.query.filter_by(user_id=int(user_id)).first()
                return user.is_admin
            except:
                return False
        return dict(is_user_admin=is_user_admin)

    return app


if __name__ == "__main__":
    app = main()
    port = int(os.environ.get("API_PORT", 5000))
    app.run(host=os.environ.get("API_IP", "0.0.0.0"), port=port)
