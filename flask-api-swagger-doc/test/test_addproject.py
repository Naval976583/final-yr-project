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
        response = tester.get("/addproject")
        statuscode = response.status_code
        self.assertIn(statuscode, (201, 400))

    # Check for Response is a json file or not
    def test_index_content(self):
        tester = app.test_client(self)
        response = tester.get("/addproject")
        self.assertEqual(response.content_type, "application/json")

    def test_index_data(self):
        tester = app.test_client(self)
        response = tester.get("/addproject")
        self.assertTrue(b'"project name should be unique"' in response.data)


if __name__ == "__main__":
    unittest.main()
