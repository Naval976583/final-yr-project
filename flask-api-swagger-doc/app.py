import datetime
from enum import unique

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from bson import ObjectId
from bson import json_util
from marshmallow import Schema, fields
from pymongo import MongoClient, ASCENDING
from flask import Flask, request, jsonify, render_template, send_from_directory
from jinja2 import Environment, FileSystemLoader
import json
import requests
from flask_mail import Mail, Message
from email.mime.multipart import MIMEMultipart
from static import payload, updated_data
import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)

app = Flask(__name__, template_folder="./swagger/templates")

# Establish a connection to the MongoDB server and the project collection
client = MongoClient('localhost', 27017)
db = client['dcforms']
project_collection = db['projects']


# Adding Project---Question1

@app.route('/addproject', methods=['POST'])
def add_project():
    if ('prj_name' not in payload) or ('customer_id' not in payload) or ('created_by' not in payload):
        return jsonify({'error': 'prj_name, customer_id, and created_by are mandatory fields'}), 400

    if project_collection.find_one({'prj_name': payload['prj_name']}) is not None:
        return jsonify({'error': 'project name should be unique'}), 400

    # Insert the payload document into the project collection
    headers = {'Content-Type': 'application/json'}
    # project_collection.create_index([('prj_name', ASCENDING)],unique = True)
    project_collection.create_index([('prj_name', ASCENDING)])
    result = project_collection.insert_one(payload)

    return jsonify({'message': 'project added successfully', 'project_id': str(result.inserted_id)}), 201


@app.route("/update", methods=['POST'])
def update_project():
    # _json = request.get_json()
    _json = updated_data

    _p_name = _json['prj_name']
    _p_id = _json['prj_id']
    _p_addr = _json['prj_addr']
    _p_loc = _json['prj_loc_state']
    _p_state = _json['prj_state']
    _c_id = _json['customer_id']
    _c_by = _json['created_by']
    _p_desc = _json['prj_desc']

    is_prj = db.projects.find_one({"prj_name": _p_name})

    if is_prj is not None:
        db.projects.update_one({"prj_name": _p_name}, {'$set': {

            "web_users": _json['web_users'],
            "prj_loc_city": _json['prj_loc_city'],
            "created_on": datetime.utcnow(),
            "prj_desc": _p_desc,
            "prj_loc_country": _json['prj_loc_country'],
            "customer_id": _c_id,
            "prj_name": _p_name,
            "prj_date": _json['prj_date'],
            "prj_id": _p_id,
            "created_by": _c_by,
            "prj_addr": _p_addr,
            "prj_loc_state": _p_loc,
            "prj_state": _p_state

        }})

        resp = jsonify("user updated successfully")

        resp.status_code = 200

        return resp
    else:
        return jsonify("project not found")


# Deleting Project and all associated forms --- Question2


@app.route('/delete/<id>',methods=['GET'])
def delete_user(id):
    proj_doct = project_collection.find_one({'_id': ObjectId(str(id))})

    if proj_doct is None:
        return jsonify({'error': 'project not found'}), 404

    # Delete all lookup forms documents associated with the project ID
    db.forms.delete_many({'project_id': ObjectId(id)})

    # Delete formdata
    db.formdata.delete_many({'projectId': str(id)})

    # Delete the project document
    project_collection.delete_one({'_id': ObjectId(id)})

    return jsonify({'message': 'project and associated lookup forms deleted successfully'}), 200


def json_handler(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


app.json_encoder = JSONEncoder


# Listing All latest documents by given projections --- Question3
@app.route('/find3', methods=['GET'])
def find_user3():
    result = redis_client.get("find3")
    if result is not None:
        return jsonify(json.loads(result))
    doc = db.projects.aggregate([
        {
            "$match":
                {
                    "customer_id": 28,
                    "created_on":
                        {
                            "$gt": datetime.datetime(2019, 12, 31), "$lte": datetime.datetime(2020, 12, 31)
                        }
                }
        },
        {
            "$project": {
                "prj_id": {"$toString": "_id"},
                "prj_name": 1,
                "customer_id": 1,
                "created_on": {"$dateToString": {"format": "%d-%m-%Y", "date": "$created_on"}
                               },

            }},
        {
            "$sort": {
                "created_on": -1,
            }
        }
    ])

    # result stored in redis for fast fetching of data

    result = json.loads(json_util.dumps(list(doc)))  # serialize ObjectId to string
    redis_client.set("find3", json.dumps(result))
    result = json.loads(redis_client.get("find3"))
    return jsonify(list(result))


# ----Question 4

@app.route("/find4")
def find_user4():
    result = redis_client.get("find4")
    if result is not None:
        return jsonify(json.loads(result))
    doc = db.projects.aggregate([
        {
            "$match":
                {
                    "customer_id": 28,
                    "created_on":
                        {
                            "$lte": datetime.datetime(2022, 6, 11)
                        }
                }
        },
        {
            '$lookup': {
                'from': 'forms',
                'localField': '_id',
                'foreignField': 'project_id',
                'as': 'forms'
            }

        },
        {
            "$unwind":
                "$forms"
        },
        {
            "$project": {
                "forms._id": {"$toString": "forms._id"},
                "forms.form_name": 1,
                "forms.form_desc": 1,
                "created_on": {"$dateToString": {"format": "%d-%m-%Y", "date": "$created_on"}},
            }
        },
        {
            "$sort": {
                "created_on": -1,
            }
        }
    ])
    # result stored in redis for fast fetching of data

    result = json.loads(json_util.dumps(list(doc)))  # serialize ObjectId to string
    redis_client.set("find4", json.dumps(result))
    result = json.loads(redis_client.get("find4"))
    return jsonify(list(result))

    # result = [json.loads(json.dumps(doc, default=str)) for doc in list(doc)]
    # return jsonify(result)


# insert api to insert data in students and send mail
app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='naval976583@gmail.com',
    MAIL_PASSWORD='ezkbjdqxxuetwiwd',
))

mail = Mail(app)


@app.route('/insertdata', methods=['POST'])
def insert_student():
    # student = request.json
    student = {"first_name": "Vishal", "middle_name": "Digambar", "last_name": "Patil",
               "email": "naval976583@gmail.com",
               "phone_no": "9112837969", "dob": "10012002", "collage": "GCOEJ", "stream": "CSE", "year": "LY",
               'last_update': datetime.datetime.today().strftime('%Y-%m-%d')}

    html = render_template('Student_Email.html', student=student)

    db.students.insert_one(student)
    # mail:"arjun.n@digicollect.com"
    email_data = {
        "to": ["naval976583@gmail.com"],
        "from": "naval976583@gmail.com",
        "cc": [],
        "bcc": [],
        "subject": "STUDENT DETAILS",
        "name": "Student Details",
        "content": "Student details added successfully",
        "reply_to": None
    }

    msg = Message(email_data['subject'], sender=email_data['from'], recipients=email_data['to'])
    msg.body = email_data['content']
    msg.html = html
    mail.send(msg)

    requests.post('https://email.digicollect.com/sendgrid/send_mail',
                  headers={"Content-Type": "application/json"},
                  json=email_data).json()

    resp = jsonify("Student details added successfully")
    resp.status_code = 200
    return resp


# Displaying all projects with associated forms --- Question 5
# Has bug need to figure it out
@app.route("/displaydata")
def display_data():
    result = redis_client.get("displaydata")
    if result is not None:
        return jsonify(json.loads(result))
    doc = db.formdata.aggregate([
        {
            '$addFields': {
                'formId': {
                    '$toObjectId': '$formId'
                }
            }
        }, {
            '$lookup': {
                'from': 'forms',
                'localField': 'formId',
                'foreignField': '_id',
                'as': 'forms'
            }
        }, {
            '$addFields': {
                'projectId': {
                    '$toObjectId': '$projectId'
                }
            }
        }, {
            '$lookup': {
                'from': 'projects',
                'localField': 'projectId',
                'foreignField': '_id',
                'as': 'projects'
            }
        }, {
            '$project': {
                'approved_by': 1,
                'createdby': 1,
                'firstname': 1,
                'form_status': 1,
                'last_name': 1,
                'sentby': 1,
                'sentby_name': 1,
                'submission_type': 1,
                'submitted_date': 1,
                'user_id': 1,
                'user_type': 1,

                # 'forms': {
                #     '$arrayElemAt': ['$forms', 0]
                # },
                # 'projects': {
                #     '$arrayElemAt': ['$projects', 0]
                # }
                'forms': {
                    'form_name': 1,
                    '_id': 1
                },
                'projects': {
                    'prj_name': 1,
                    '_id': 1
                }
            }
        }
    ])
    # result stored in redis for fast fetching of data
    result = redis_client.get("displaydata")
    if result is None:
        result = json.loads(json_util.dumps(list(doc)))  # serialize ObjectId to string
        redis_client.set("displaydata", json.dumps(result))
        result = json.loads(redis_client.get("displaydata"))
        return jsonify(list(result))
    else:
        return result
    # return jsonify(list(doc))


if __name__ == "__main__":
    app.debug = True
    app.run()
