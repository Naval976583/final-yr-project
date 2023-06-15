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
        response = tester.get("/update")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertIn(response.data, (b'"user updated successfully"\n', b'"project not found"\n'))

    # Check for Response is a json file or not
    def test_index_content(self):
        tester = app.test_client(self)
        response = tester.get("/update")
        self.assertEqual(response.content_type, "application/json")


if __name__ == "__main__":
    unittest.main()
