from flask import Blueprint, render_template
from flask_login import login_required

tutorial_bp = Blueprint('tutorial', __name__, url_prefix='/tutorial')

@tutorial_bp.route('/')
@login_required
def index():
    return render_template('tutorial.html')
