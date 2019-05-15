from flask import Blueprint, render_template

# error_handle = Blueprint('error_handle', __name__, template_folder='templates')


# @error_handle.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
