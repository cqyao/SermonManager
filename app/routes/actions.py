from flask import Blueprint, request
import git

actions_bp = Blueprint('actions', __name__)

# FOR GITHUB CI/CD AUTOMATION
@actions_bp.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('./SermonManager')
        origin = repo.remotes.origin
        
        origin.pull()
        return 'updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400