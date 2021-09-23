from .base_test import BaseTest
from . import RestFramework

class TestInitApp(BaseTest):
    
    def test_init_app(self):
        # self.app.config.from_pyfile()
        # empty app config
        rf = RestFramework()
        rf.init_app(self.app)
        self.assertIn("extensions", dir(self.app))
