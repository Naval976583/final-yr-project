import datetime
from enum import unique
from bson import ObjectId
from bson import json_util
from pymongo import MongoClient, ASCENDING
from flask import Flask, request, jsonify, render_template
from jinja2 import Environment, FileSystemLoader
import json
import requests


# Establish a connection to the MongoDB server and the project collection
client = MongoClient('localhost', 27017)
db = client['dcforms']
project_collection = db['projects']
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


# Define a function to handle the POST request for adding a new project
app = Flask(__name__)
app.json_encoder = JSONEncoder



# Adding Project---Question1
@app.route('/addproject', methods=['GET','POST'])
def add_project():
    payload = request.get_json()

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



#updating project- has bug need to update entire code

@app.route("/update", methods=['POST'])
def update_project():
    _json = request.get_json()

    _p_name = _json['prj_name']
    _p_id = _json['prj_id']
    _p_addr = _json['prj_addr']
    _p_loc = _json['prj_loc_state']
    _p_state = _json['prj_state']
    _c_id = _json['customer_id']
    _c_by = _json['created_by']
    _p_desc = _json['prj_desc']

    is_prj = db.projects.find_one({"prj_name": _p_name})

    # doc = list(db.projects.aggregate([
    #     {"$match":
    #          {"prj_name": _p_name}
    #      },
    #     {"$project": {
    #         "_id": 0,
    #         "idAsString": {'$toString': "$_id"}}}
    #
    # ]))
    # id = doc[0]["idAsString"]
    # print(id)
    if is_prj is not None :

        # _json['prj_date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        # _json['web_user_info.date_added'] = datetime.datetime.now()
        # _json['created_on'] = datetime.datetime.now()
        # for i in _json['mobile_users_info']:
        #     if [i['date_added']]:
        #         i['date_added'] = datetime.datetime.now()


        db.projects.update_one({"_id": ObjectId(id)}, {'$set': {

            "web_users": _json['web_users'],
            "prj_loc_city": _json['prj_loc_city'],
            "web_users_info": _json['web_users_info'],
            "created_on": _json['created_on'],
            "prj_desc": _p_desc,
            "prj_loc_country": _json['prj_loc_country'],
            "mobile_users_info": _json['mobile_users_info'],
            "customer_id": _c_id,
            "prj_name": _p_name,
            "prj_date": _json['prj_date'],
            "prj_id": _p_id,
            "created_by": _c_by,
            "prj_addr": _p_addr,
            "prj_loc_state": _p_loc,
            "prj_state": _p_state

        }})

        resp = jsonify("user updated sucessfully")

        resp.status_code = 200

        return resp
    else:
        return jsonify("project not found")


# Set up Jinja2 to load templates from the templates folder
env = Environment(loader=FileSystemLoader('templates'))

# Load the email template from the student_details.html file
template = env.get_template('student_details.html')

#Inserting document in forms api
@app.route("/insert",methods=['POST','GET'])
def insert():
    # Define the student_info dictionary with the values to replace the placeholders
    student_info = {
        "name": "John",
        "student_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 555-1234",
        "address": "123 Main St, Anytown USA",
        "sender_name": "Jane"
    }

    # Use Jinja2 to render the email template with the student_info dictionary
    content = template.render(student_info)

    # Use the rendered email content in the email_data dictionary
    email_data = {
        "to": ["naval976583@gmail.com"],
        "from": "",
        "cc": [],
        "bcc": [],
        "subject": "Student Details",
        "name": "Student Details",
        "content": content,
        "reply_to": None
    }

    # Use requests.post to send the email
    response = requests.post('https://naval.dp@digicollect.com/sendgrid/send_mail',
                             headers={"Content-Type": "application/json"},
                             json=email_data)
    return response
    if response["status_id"] == 1:
        return f"Email sent successfully!"
    else:
        return f"Error sending email:", response.content





# Deleting Project and all associated forms --- Question2


@app.route('/delete/<id>')
def delete_user(id):
    proj_doct = project_collection.find_one({'_id': ObjectId(str(id))})

    if proj_doct is None:
        return jsonify({'error': 'project not found'}), 404

    # Delete the project document
    project_collection.delete_one({'_id': ObjectId(id)})

    # Delete all lookup forms documents associated with the project ID
    db.forms.delete_many({'project_id': ObjectId(id)})

    # Delete formdata
    db.formdata.delete_many({'projectId':str(id)})


    return jsonify({'message': 'project and associated lookup forms deleted successfully'}), 200



# @app.route('/listdoc', methods=['GET', 'POST'])
# def list_doc():
#     doc = db.projects.aggregate([
#         {"$match": {
#             "customer_id": 28,
#             "created_on": {"$gte": datetime.datetime(2020, 1, 1)
#                            }
#         }
#         },
#         {"$project": {
#             "prj_id": 1,
#             "prj_name": 1,
#             "customer_id": 1,
#             "created_on": {"$dateToString": {"format": "%d-%m-%Y", "date": "$created_on"}
#                            },
#             "_id": 0
#         }
#         },
#         {"$sort": {"created_on": -1}
#          }
#     ])
#     return jsonify(list(doc))



#Displaying all projects with associated forms --- Question 5
#Has bug need to figure it out
@app.route("/displaydata")
def display_data():
    # doc = db.formdata.aggregate([
    #     {
    #         '$addFields': {
    #             'formId': {
    #                 '$toObjectId': '$formId'
    #             }
    #         }
    #     }, {
    #         '$lookup': {
    #             'from': 'forms',
    #             'localField': 'formId',
    #             'foreignField': '_id',
    #             'as': 'forms'
    #         }
    #     }, {
    #         '$addFields': {
    #             'projectId': {
    #                 '$toObjectId': '$projectId'
    #             }
    #         }
    #     }, {
    #         '$lookup': {
    #             'from': 'projects',
    #             'localField': 'projectId',
    #             'foreignField': '_id',
    #             'as': 'projects'
    #         }
    #     }, {
    #         '$project': {
    #             '_id': 1,
    #             'approved_by': 1,
    #             'createdby': 1,
    #             'form_status': 1,
    #             'sentby': 1,
    #             'sentby_name': 1,
    #             'submission_type': 1,
    #             'submitted_date': 1,
    #             'user_id': 1,
    #             'user_type': 1,
    #             'forms': {
    #                 '$arrayElemAt': ['$forms', 0]
    #             },
    #             'projects': {
    #                 '$arrayElemAt': ['$projects', 0]
    #             }
    #         }
    #     }
    # ])
    return jsonify(json.loads(json_util.dumps(list(doc), json_options=json_util.JSONOptions(datetime_representation=json_util.ISO8601))), cls=CustomJSONEncoder)

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
    return jsonify(list(doc))




# Listing All latest documents by given projections --- Question3
@app.route('/find3', methods=['GET', 'POST'])
def find_user3():
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
            "$sort":{
        "created_on":-1,
    }
        }
    ])
    return jsonify(list(doc))


#----Question 4

@app.route("/find4")
def find_user4():
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

    result = [json.loads(json.dumps(doc, default=str)) for doc in list(doc)]
    return jsonify(result)










if __name__ == "__main__":
    app.debug = True
    app.run()


