from flask import Flask
import unittest
from . import RestFrame

class TestInitApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Flask(__name__)
        return super().setUpClass()

    def setUp(self) -> None:
        self.context = self.app.test_request_context()
        self.context.push()
        return super().setUp()
    
    def tearDown(self) -> None:
        self.context.pop()
        return super().tearDown()
    
    def test_init_app(self):
        # self.app.config.from_pyfile()
        # empty app config
        restframe = RestFrame()
        restframe.init_app(self.app)
        self.assertIn("extensions", dir(self.app))
