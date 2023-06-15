try:
    import sys
    import os

    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import unittest
    from app import app
    from app import project_collection


except Exception as e:
    print("some modules are Missing".format(e))


class FlaskTest(unittest.TestCase):
    first_document = project_collection.find_one({})
    id = first_document["_id"]

    # Check for Response 200 or 404
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/delete/" + str(self.id))
        statuscode = response.status_code
        self.assertIn(statuscode, (200, 404))

    # Check for Response is a json file of not
    def test_index_content(self):
        tester = app.test_client(self)
        response = tester.get("/delete/" + str(self.id))
        self.assertEqual(response.content_type, "application/json")


if __name__ == "__main__":
    unittest.main()
