from flask_sqlalchemy import SQLAlchemy
from uwsgidecoratorsfallback import postfork

db = SQLAlchemy()


def setup_db(app):
    db.app = app
    db.init_app(app)


@postfork
def reset_db_connections():
    with db.app.app_context():
        print("[POSTFORK] Restarting Postgres sessions")
        db.session.close_all()
        db.engine.dispose()
        db.create_scoped_session()
