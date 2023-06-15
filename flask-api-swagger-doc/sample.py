class ExampleResponseSchema(Schema):
    """
    Swagger response schema for the example API endpoint
    """
    type = 'array'
    items = {
        'type': 'object',
        'properties': {
            '_id': {'type': 'string'},
            'approved_by':{'type': 'string'},
            'createdby':{'type': 'string'},
            'form_status':{'type': 'string'},
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
            'sentby' : {'type':'string'},
            'sentby_name':{'type':'string'},
            'submission_type':{'type':'string'},
            'submitted_date':{'type':'datetime'},
            'user_id':{'type':'string'},
            'user_type':{'type':'string'}
        }
    }

