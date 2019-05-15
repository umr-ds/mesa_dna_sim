# init SQLAlchemy so we can use it later in our models
# db = SQLAlchemy()

"""
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["DEBUG"] = True

    # app.config['SECRET_KEY'] = 'Jdw)!4r3910dJOPSfdja'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # db.init_app(app)

    # blueprint for auth routes in our app
    # from api.auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)

    app.register_blueprint(main_page)
    app.register_error_handler(404, page_not_found)

    from database import db
    db.init_app(app)

    return app


from api import models
"""