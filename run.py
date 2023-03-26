import sys
from pathlib import Path
from werkzeug.middleware.dispatcher import DispatcherMiddleware # use to combine each Flask app into a larger one that is dispatched based on prefix
from werkzeug.serving import run_simple # werkzeug development server


from main import app as flask_app_1

def create_and_run_app():
    application = DispatcherMiddleware(flask_app_1)

    #TODO if you want to run on https
    # run_simple('0.0.0.0', 5000, application, use_reloader=True, use_debugger=True, use_evalex=True, ssl_context='adhoc')

    #Run on http
    run_simple('0.0.0.0', 5000, application, use_reloader=True, use_debugger=True, use_evalex=True)

if __name__ == "__main__":
	app = create_and_run_app()
