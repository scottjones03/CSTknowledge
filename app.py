from flask import * #importing flask (Install it using python -m pip install flask)
from werkzeug.utils import secure_filename
import os
import queue
from gpt4_api import GPT4API
from notionAPI import NotionAPI
from threading import Thread
from private import NOTION_TOKEN, PROMPTS, SESSION_TOKEN
import time
import queue
from automationGPT import ChatGPT

def create_app():
    app = Flask(__name__)
    # more setup here...
    return app

app = Flask(__name__) #initialising flask
app.config['UPLOAD_FOLDER'] = '/Users/scottjones_admin/Library/Mobile Documents/com~apple~CloudDocs/Mac files/Repos/CSTKnowledge/uploaded_pdfs'  # Update this to your desired upload path
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

jobsQueue: queue.Queue

@app.route("/") #defining the routes for the home() funtion (Multiple routes can be used as seen here)
@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("home.html") #rendering our home.html contained within /templates

@app.route("/account", methods=["POST", "GET"])
def account():
    usr = "<User Not Defined>"
    pdf = []
    if request.method == "POST":
        usr = request.form.get("name", "<User Not Defined>")
        
        # Check if a file was uploaded
        if 'pdfFile' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)

        files = request.files.getlist('pdfFile')

        # If no file is selected
        if len(files) == 0 or files[0].filename == '':
            flash('No file selected')
            return redirect(request.url)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                p = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(p)
                pdf.append(filename)
                jobsQueue.put((filename, p))
            else: 
                pdf.append("<File Not Defined>")
    return render_template('account.html', username=usr, pdfName=pdf)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']




def runAPP(jobs: queue.Queue): #checking if __name__'s value is '__main__'. __name__ is an python environment variable who's value will always be '__main__' till this is the first instatnce of app.py running
    global jobsQueue
    jobsQueue=jobs
    app.run(debug=True,port=4949) #running flask (Initalised on line 4)



def run_pdf_tasks(jobsqueue: queue.Queue, api: ChatGPT):
    prompts = [PROMPTS[-1]]
    first_chunk_idxs = [0,0]
    notionapi = NotionAPI(NOTION_TOKEN)
    gpt4api = GPT4API(api, SESSION_TOKEN, notionapi)

    while True:
        item = jobsqueue.get()  # This will block until an item is available
        
        if item is None:  # We use 'None' as a signal to stop
            time.sleep(30)
            continue
        gpt4api.parsePDF(item[0], item[1], prompts, first_chunk_idxs)
        jobsqueue.task_done()

if __name__ == "__main__":
    api = ChatGPT(SESSION_TOKEN)
    jobs = queue.Queue()
    thread1 = Thread(target=run_pdf_tasks, args=(jobs,api,))
    thread1.start()
    runAPP(jobs)
    jobs.put(None)
    thread1.join()