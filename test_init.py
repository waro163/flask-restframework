from .test import BaseTest
from . import RestFrame

class TestInitApp(BaseTest):
    
    def test_init_app(self):
        # self.app.config.from_pyfile()
        # empty app config
        restframe = RestFrame()
        restframe.init_app(self.app)
        self.assertIn("extensions", dir(self.app))
