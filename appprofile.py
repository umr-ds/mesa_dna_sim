#!flask/bin/python
from werkzeug.contrib.profiler import ProfilerMiddleware
import app as appl


def profile():
    app = appl.main()

    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[80])
    app.run(debug=True)


if __name__ == "__main__":
    profile()
