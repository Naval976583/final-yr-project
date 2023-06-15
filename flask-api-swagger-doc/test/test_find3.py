try:
    import sys
    import os

    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import unittest
    import app
    from app import app

except Exception as e:
    print("some modules are Missing".format(e))


class FlaskTest(unittest.TestCase):
    # Check for Response 200
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/find3")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    # Check for Response is a json file of not
    def test_index_content(self):
        tester = app.test_client(self)
        response = tester.get("/find3")
        self.assertEqual(response.content_type, "application/json")


if __name__ == "__main__":
    unittest.main()
