#---------------------------------------
# TODO API
# Version 1.0
#---------------------------------------

# import required modules
from flask import Flask, Response
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
dbconnect = DBConnector("3.130.5.83",9271)

# send HTTP Response
def responsify(status,message,data={}):
    code = int(status)
    a_dict = {"data":data,"message":message,"code":code}
    try:
        return Response(json.dumps(a_dict), status=code, mimetype='application/json')
    except:
        return Response(str(a_dict), status=code, mimetype='application/json')

# create a new task
@app.route("/todo/api/v1/new-task/<path:task_name>")
def new_task(task_name):
    dbconnect.dbTask("new_record","todo-task",{},{"name":task_name,"status":0})
    return responsify(dbconnect.response.status_code,"Task Created",dbconnect.response.json()["data"])

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

# fetch tasks
@app.route("/todo/api/v1/fetch-tasks")
def fetch_tasks():
    dbconnect.dbTask("fetch_records","todo-task",{})
    return responsify(dbconnect.response.status_code,"All Tasks",dbconnect.response.json()["data"])

if __name__ == "__main__":
    app.run()
