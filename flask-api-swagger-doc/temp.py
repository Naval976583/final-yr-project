from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, jsonify, render_template, send_from_directory, request
from marshmallow import Schema, fields
from werkzeug.utils import secure_filename
from pymongo import MongoClient, ASCENDING
import redis
from static import payload, updated_data
import datetime
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

spec = APISpec(
    title='Mongodb-flask-api-swagger-doc',
    version='1.0.0',
    openapi_version='3.0.2',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)


@app.route('/api/swagger.json')
def create_swagger_spec():
    return jsonify(spec.to_dict())


class MyRequestSchema1(Schema):
    web_users = fields.List(fields.Integer())
    prj_loc_city = fields.String()
    web_users_info = fields.List(fields.Nested(lambda: WebUserInfoSchema()))
    created_on = fields.DateTime()
    prj_desc = fields.String()
    prj_loc_country = fields.String()
    mobile_users_info = fields.List(fields.Nested(lambda: MobileUserInfoSchema()))
    customer_id = fields.Integer()
    prj_name = fields.String()
    prj_date = fields.String()
    prj_id = fields.String()
    created_by = fields.Integer()
    prj_addr = fields.String()
    prj_loc_state = fields.String()
    prj_state = fields.String()


class WebUserInfoSchema(Schema):
    date_added = fields.DateTime()
    user_id = fields.Integer()
    who_added = fields.Integer()


class MobileUserInfoSchema(Schema):
    date_added = fields.DateTime()
    user_id = fields.Integer()
    who_added = fields.Integer()

class MyResponseSchema(Shema):
    message = fields.String()

@app.route('/addproject', methods=['POST'])
def add_project():
    """
        Adding Project to database
        ---
        post:
            description: Add Project description
            requestBody:
                required: true
                content:
                    application/json:
                        schema: MyRequestSchema1
            responses:
                201:
                    description: Success- Project Added Successfully
                    content:
                        application/json:
                            schema: MyResponseSchema
                400:
                    description: Bad Request
        """

    if ('prj_name' not in payload) or ('customer_id' not in payload) or ('created_by' not in payload):
        return jsonify({'error': 'prj_name, customer_id, and created_by are mandatory fields'}), 400

    if project_collection.find_one({'prj_name': payload['prj_name']}) is not None:
        message = {'error': 'project name should be unique'}
        return MyResponseSchema().dump({'message': message})
        # return jsonify({'error': 'project name should be unique'}), 400

    # Insert the payload document into the project collection
    headers = {'Content-Type': 'application/json'}
    # project_collection.create_index([('prj_name', ASCENDING)],unique = True)
    project_collection.create_index([('prj_name', ASCENDING)])
    result = project_collection.insert_one(payload)

    message = {'message': 'project added successfully', 'project_id': str(result.inserted_id)}
    return MyResponseSchema().dump({'message': message})

    # return jsonify({'message': 'project added successfully', 'project_id': str(result.inserted_id)}), 201


class MyRequestSchema2(Schema):
    web_users = fields.List(fields.Integer())
    prj_loc_city = fields.String()
    created_on = fields.Dict()
    prj_desc = fields.String()
    prj_loc_country = fields.String()
    customer_id = fields.Integer()
    prj_name = fields.String()
    prj_date = fields.String()
    created_by = fields.Integer()


@app.route("/update", methods=['POST'])
def update_project():
    """
            Updating Project in database
            ---
            post:
                description: Update Project description
                requestBody:
                    required: true
                    content:
                        application/json:
                            schema: MyRequestSchema2
                responses:
                    200:
                        description: Success- Project Updated Successfully
                        content:
                            application/json:
                                schema: MyResponseSchema
                    400:
                        description: Project Not Found
            """
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
        message = {'response': 'project updated successfully'}
        return MyResponseSchema().dump({'message': message})


    else:
        message = {'response': 'project not found'}
        return MyResponseSchema().dump({'message': message})


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


class MyResponseSchema3(Schema):
    _id = fields.String(attribute=lambda x: x['_id']['$oid'])
    created_on = fields.String()
    customer_id = fields.Integer()
    prj_id = fields.String()
    prj_name = fields.String()


# Listing All latest documents by given projections --- Question3
@app.route('/find3', methods=['GET'])
def find_user3():
    """
        Listing All latest documents by given projections
        ---
        get:
            description: Listing All latest documents by given projections
            responses:
                200:
                    description: Success- Required data fetched Successfully
                    content:
                        application/json:
                            schema: MyResponseSchema3
                400:
                    description: Error in fetching data
    """
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

    response_schema = MyResponseSchema3(many=True)
    serialized_data = response_schema.dump(result)

    return serialized_data


class ExampleResponseSchema(Schema):
    """
    Swagger response schema for the example API endpoint
    """
    type = 'array'
    items = {
        'type': 'object',
        'properties': {
            '_id': {
                'type': 'object',
                'properties': {
                    '$oid': {'type': 'string'}
                }
            },
            'created_on': {'type': 'string', 'format': 'date'},
            'forms': {
                'type': 'object',
                'properties': {
                    '_id': {'type': 'string'},
                    'form_desc': {'type': 'string'},
                    'form_name': {'type': 'string'}
                }
            }
        }
    }


class Forms(Schema):
    _id = fields.String()
    form_desc = fields.String()
    form_name = fields.String()


class MyResponseSchema4(Schema):
    _id = fields.String(attribute=lambda x: x['_id']['$oid'])
    created_on = fields.String()
    forms = fields.Nested(Forms)


@app.route("/find4", methods=['GET'])
def find_user4():
    """
    Fetching data from database and displaying it
    ---
    get:
        description: Fetching data from database and displaying it
        responses:
            200:
                description: Success- Required data fetched Successfully
                content:
                    application/json:
                        schema: MyResponseSchema4
            400:
                description: Error in fetching data
    """
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
    response_schema = ExampleResponseSchema(many=True)
    serialized_data = response_schema.dump(result)

    return serialized_data
    # return jsonify(list(result))


# insert api to insert data in students and send mail

class MyResponseSchema5(Schema):
    message = fields.Str()


class MyRequestSchema5(Schema):
    first_name = fields.Str()
    middle_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    phone_no = fields.Str()
    dob = fields.Str()
    collage = fields.Str()
    stream = fields.Str()
    year = fields.Str()
    last_update = fields.DateTime()


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
    """
    Inserting Project in database and Sending Mail
    ---
    post:
        description: Inserting Project in database and Sending Mail
        requestBody:
                    required: true
                    content:
                        application/json:
                            schema: MyRequestSchema5
        responses:
            200:
                description: Success- Project Updated Successfully
                content:
                    application/json:
                        schema: MyResponseSchema3
            400:
                description: Project Not Found
    """
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

    message = {'response': 'Email Sent Successfully'}
    return MyResponseSchema5().dump({'message': message})


# Displaying all projects with associated forms --- Question 5
class ExampleResponseSchema2(Schema):
    """
    Swagger response schema for the example API endpoint
    """
    type = 'array'
    items = {
        'type': 'object',
        'properties': {
            '_id': {'type': 'string'},
            'approved_by': {'type': 'string'},
            'createdby': {'type': 'string'},
            'form_status': {'type': 'string'},
            'created_on': {'type': 'string', 'format': 'date'},
            'forms': {
                'type': 'object',
                'properties': {
                    '_id': {
                        'type': 'object',
                        'properties': {
                            '$oid': {'type': 'string'}
                        }
                    },
                    'form_name': {'type': 'string'}
                }
            },
            'projects':
                {
                    'type': 'object',
                    'properties': {
                        '_id': {
                            'type': 'object',
                            'properties': {
                                '$oid': {'type': 'string'}
                            }
                        },
                        'prj_name': {'type': 'string'}
                    }
                },
            'sentby': {'type': 'string'},
            'sentby_name': {'type': 'string'},
            'submission_type': {'type': 'string'},
            'submitted_date': {'type': 'datetime'},
            'user_id': {'type': 'string'},
            'user_type': {'type': 'string'}
        }
    }


class Forms1(Schema):
    _id = fields.String(attribute=lambda x: x['_id']['$oid'])
    form_name = fields.String()


class Project1(Schema):
    _id = fields.String(attribute=lambda x: x['_id']['$oid'])
    form_name = fields.String()


class MyResponseSchema8(Schema):
    _id = fields.String()
    approved_by = fields.String()
    createdby = fields.String()
    form_status = fields.String()
    forms = fields.List(fields.Dict())
    projects = fields.List(fields.Dict())
    sentby = fields.String()
    sentby_name = fields.String()
    submitted_date = fields.String()
    user_id = fields.String()
    user_type = fields.String()


class MyResponseSchema7(Schema):
    _id = fields.String()
    approved_by = fields.String()
    createdby = fields.String()
    form_status = fields.String()
    forms = fields.Nested(Forms1)
    projects = fields.Nested(Project1)
    sentby = fields.String()
    sentby_name = fields.String()
    submitted_date = fields.DateTime()
    user_id = fields.Integer()
    user_type = fields.String()


@app.route("/displaydata")
def display_data():
    """
        Fetching data from database and displaying it
        ---
        get:
            description: Fetching data from database and displaying it
            responses:
                200:
                    description: Success- Required data fetched Successfully
                    content:
                        application/json:
                            schema: MyResponseSchema7
                400:
                    description: Error in fetching data
        """
    result = redis_client.get("displaydata")
    if result is not None:
        response_schema = MyResponseSchema8(many=True)
        serialized_data = response_schema.dump(result)
        return serialized_data
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

        response_schema = MyResponseSchema8(many=True)
        serialized_data = response_schema.dump(result)
        return serialized_data



    else:
        response_schema = MyResponseSchema8(many=True)
        serialized_data = response_schema.dump(result)

        return serialized_data


# Deleting Project and all associated forms --- Question2
class DeleteResponseSchema(Schema):
    message = fields.String()


@app.route('/delete/<id>', methods=['GET'])
def delete_user(id):
    """
            Deleting data from database
            ---
            get:
                parameters:
                    - in: path
                      name: id
                      description: The ID of the user to delete
                      required: true
                      schema:
                        type: string

                description: Deleting Project from database
                responses:
                    200:
                        description: Success- Project deleted Successfully
                        content:
                            application/json:
                                schema: DeleteResponseSchema
                    400:
                        description: Error in fetching data
            """
    proj_doct = project_collection.find_one({'_id': ObjectId(str(id))})

    if proj_doct is None:
        message = {'error': 'project not found'}
        return MyResponseSchema().dump({'message': message})

    # Delete all lookup forms documents associated with the project ID
    db.forms.delete_many({'project_id': ObjectId(id)})

    # Delete formdata
    db.formdata.delete_many({'projectId': str(id)})

    # Delete the project document
    project_collection.delete_one({'_id': ObjectId(id)})
    message = {'response': 'project and associated lookup forms deleted successfully'}
    return MyResponseSchema().dump({'message': message})


with app.test_request_context():
    spec.path(view=add_project)
    spec.path(view=update_project)
    spec.path(view=find_user3)
    spec.path(view=find_user4)
    spec.path(view=insert_student)
    spec.path(view=display_data)
    spec.path(view=delete_user)


@app.route('/docs')
@app.route('/docs/<path:path>')
def swagger_docs(path=None):
    if not path or path == 'index.html':
        return render_template('index.html', base_url='/docs')
    else:
        return send_from_directory('./swagger/static', secure_filename(path))


if __name__ == '__main__':
    app.run(debug=True)
