try:
    import sys
    import os

    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import unittest
    from app import app


except Exception as e:
    print("some modules are Missing".format(e))


class FlaskTest(unittest.TestCase):
    # Check for Response 201 or 400
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/insertdata")
        statuscode = response.status_code
        self.assertEqual(statuscode,200)

    # Check for Response is a json file or not
    def test_index_content(self):
        tester = app.test_client(self)
        response = tester.get("/insertdata")
        self.assertEqual(response.content_type, "application/json")

    # Check whether message received is same or not 

    def test_index_data(self):
        tester = app.test_client(self)
        response = tester.get("/insertdata")
        self.assertTrue(b'"Student details added successfully"' in response.data)


if __name__ == "__main__":
    unittest.main()
