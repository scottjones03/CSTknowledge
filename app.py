from flask import * #importing flask (Install it using python -m pip install flask)
from werkzeug.utils import secure_filename
import os
import queue
from gpt4_api import GPT4API
from notionAPI import NotionAPI
from threading import Thread
from prompts import PROMPTS
import time
import queue
import markdown2
from werkzeug.security import check_password_hash
from flask_login import login_user
from pdfid.pdfid import PDFiD
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

import xml.etree.ElementTree as ET


# Create the LoginManager instance
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    login_manager.init_app(app)  # Initialize it for your application
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    return app



def is_pdf_safe(pdf_path):
    """Run PDFiD on the PDF and check the output for signs of exploits."""
    xmlcontent = PDFiD(pdf_path)

    # Parse the XML content into an ElementTree
    root = ET.fromstring(xmlcontent.toxml())

    # Search for 'JS' and 'JavaScript' tags
    js_elements = root.findall('.//JS')
    javascript_elements = root.findall('.//JavaScript')

    # Then check counts
    if len(js_elements) > 0 or len(javascript_elements) > 0:
        return False

    return True



app = create_app()
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER') 
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['TEXT_FOLDER'] = os.environ.get('TEXT_FOLDER')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////tmp/{os.environ.get("DATABASE_ID")}.db'  # replace with your DB URI
app.config['USER']=[os.environ.get('USER')]
app.config['PASSWORD']={os.environ.get('USER'): os.environ.get('PASSWORD')}


NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
SESSION_PATH = os.environ.get("SESSION_TOKEN")

db = SQLAlchemy(app)


# Update your User model to inherit from UserMixin, which includes required methods
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    filenames = db.relationship('Filename', backref='user', lazy=True)

class Filename(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
with app.app_context():
    db.create_all()
@app.route("/view_file/<filename>", methods=["GET"])
def view_file(filename):
    with open(os.path.join(app.config['TEXT_FOLDER'], filename), 'r', encoding='utf-8') as file:
        file_content = file.read()
    html_content = markdown2.markdown(file_content)  # convert Markdown to HTML
    return render_template('view_file.html', filename=filename, file_content=html_content)

@app.route("/") #defining the routes for the home() funtion (Multiple routes can be used as seen here)
@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("home.html") #rendering our home.html contained within /templates

@app.route("/account", methods=["POST", "GET"])
def account():
    usr = "<User Not Defined>"
    filenames = []
    startIndex =0
    if request.method == "POST":
        usr = request.form.get("name", "<User Not Defined>")
        password = request.form.get("password")
        selected_model = request.form.get("modelSelect", "3")
        
        if usr in app.config["USER"] and password==app.config["PASSWORD"][usr]: 
            user = User.query.filter_by(name=usr).first()
            if not user:
                user = User(name=usr)
                db.session.add(user)
                db.session.commit()

            login_user(user, remember=True)
            # further processing...
        else:
            flash('Invalid username or password')
            return redirect(request.url)
        startIndex = int(request.form.get("spinBox1", 0))
        # Check if a file was uploaded
        if 'pdfFile' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)

        files = request.files.getlist('pdfFile')
  
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(usr+'--'+file.filename)
                p = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(p)
                
                db_filename = Filename(name=filename, user_id=user.id)
                db.session.add(db_filename)
                db.session.commit()
                if not is_pdf_safe(p):
                    flash('Potentially unsafe file blocked')
                    return redirect(request.url)
                filenames.append(filename)
                jobsQueue.put((filename, p, startIndex, usr, selected_model))
            else: 
                filenames.append("<File Not Defined>")
    q=User.query.filter_by(name=usr).first()
    if q:
        return render_template('account.html', username=usr, filenames=[f.name for f in q.filenames if f])
    else:
        return render_template('account.html', username=usr, filenames=[])



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']




def runAPP(jobs: queue.Queue): #checking if __name__'s value is '__main__'. __name__ is an python environment variable who's value will always be '__main__' till this is the first instatnce of app.py running
    global jobsQueue
    jobsQueue=jobs
    app.run(debug=False,port=4949) #running flask (Initalised on line 4)



def run_pdf_tasks(jobsqueue: queue.Queue):
    prompts = [PROMPTS[-1]]
    notionapi = NotionAPI(NOTION_TOKEN)
    with open(SESSION_PATH, 'r') as f:
        token = f.read()
    gpt4api = GPT4API(token, notionapi, model='4')
    gpt3api = GPT4API(token, notionapi, model='3')
    while True:
        try:
            item = jobsqueue.get()  # This will block until an item is available
            if item is None:  # We use 'None' as a signal to stop
                time.sleep(30)
                continue

            with ThreadPoolExecutor(max_workers=1) as executor:
                if item[3]=='4':
                    future = executor.submit(gpt4api.parsePDF, item[0], item[1], prompts, item[2])
                else:
                    future = executor.submit(gpt3api.parsePDF, item[0], item[1], prompts, item[2])
                future.result(timeout=1800)  # 30 minutes timeout for the task to complete
            jobsqueue.task_done()
        except TimeoutError:
            notionapi = NotionAPI(NOTION_TOKEN)
            gpt4api = GPT4API(SESSION_PATH, notionapi, model='4')
            gpt3api = GPT4API(SESSION_PATH, notionapi, model='3')
            print(f'Task took too long to complete. Restarting the task for item: {item}')
            jobsqueue.put(item)  # Putting the item back in queue to retry
            continue

if __name__ == "__main__":
    jobs = queue.Queue()
    while True:
        try:
            thread1 = Thread(target=run_pdf_tasks, args=(jobs,))
            thread1.start()
            runAPP(jobs)
        except Exception as e:
            print(e)
        