from flask import Flask
import unittest

class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Flask(__name__)
        return super().setUpClass()

    def setUp(self) -> None:
        self.context = self.app.test_request_context()
        self.context.push()
        self.client = self.app.test_client()
        return super().setUp()
    
    def tearDown(self) -> None:
        self.context.pop()
        return super().tearDown()