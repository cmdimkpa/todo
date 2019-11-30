#---------------------------------------
# TODO API
# Version 1.0
#---------------------------------------

# import required modules
from flask import Flask, Response, render_template, request, redirect
from flask_cors import CORS
import requests as http
import json

# create flask application
app = Flask(__name__)
CORS(app)

# Database Connector class
class DBConnector:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.base_url = "http://%s:%s/ods/"%(self.host,self.port)
        self.response = None
    def dbTask(self,task,table,constraints={},data={}):
        process_url = self.base_url+task
        payload = {
            "tablename":table,
            "data":data,
            "constraints":constraints
        }
        self.response = http.post(process_url,json.dumps(payload),headers={"Content-Type":"application/json"})

# database connector (instance of class pointing to target host and port)
dbconnect = DBConnector("localhost",9271)

# send HTTP Response
def responsify(status,message,data={}):
    code = int(status)
    a_dict = {"data":data,"message":message,"code":code}
    try:
        return Response(json.dumps(a_dict), status=code, mimetype='application/json')
    except:
        return Response(str(a_dict), status=code, mimetype='application/json')

# create a new task
def new_task(task_name):
    dbconnect.dbTask("new_record","todo-task",{},{"name":task_name,"status":0})
    return dbconnect.response.status_code

# remove a task
@app.route("/todo/api/v1/remove-task/<path:task_name>")
def remove_task(task_name):
    dbconnect.dbTask("delete_records","todo-task",{"name":task_name})
    return responsify(dbconnect.response.status_code,"Task Removed",dbconnect.response.json()["data"])

# complete a task
@app.route("/todo/api/v1/complete-task/<path:task_name>")
def complete_task(task_name):
    dbconnect.dbTask("update_records","todo-task",{"name":task_name},{"status":1})
    return responsify(dbconnect.response.status_code,"Task Completed",dbconnect.response.json()["data"])

# serve files
@app.route("/files/<path:filename>")
def get_file(filename):
    try:
        return app.send_static_file(filename)
    except:
        return "<h1> Error Serving File: %s <h1>" % filename

# fetch tasks
def fetch_tasks():
    dbconnect.dbTask("fetch_records","todo-task",{})
    return dbconnect.response.json()["data"]

def generate_button(text,status):
    colors = {0:"#ff0000",1:"#4CAF50"}
    button = '<button class="button" style="background-color:%s" data-status="%s">%s</button><br>' % (colors[status],status,text)
    return button

def get_dynamic():
    all_tasks = fetch_tasks()
    UNDONE_TASKS_HTML = ""; done_array = []
    for task in all_tasks:
        if task["status"]:
            done_array.append(generate_button(task["name"],task["status"]))
        else:
            UNDONE_TASKS_HTML+=generate_button(task["name"],task["status"])
    DONE_TASKS_HTML = "".join(done_array[::-1])
    return UNDONE_TASKS_HTML,DONE_TASKS_HTML

# render page
@app.route("/todo.app")
def render_page():
    UNDONE_TASKS_HTML,DONE_TASKS_HTML = get_dynamic()
    return render_template("todo.html",UNDONE_TASKS_HTML=UNDONE_TASKS_HTML,DONE_TASKS_HTML=DONE_TASKS_HTML)

# form input
@app.route("/todo/api/v1/post")
def form():
    task_name = dict(request.args)["mydata"][0]
    status = new_task(task_name)
    return redirect("http://localhost:5000/todo.app",302)

if __name__ == "__main__":
    app.run()
