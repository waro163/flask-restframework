from .base_test import BaseTest, BaseFuncTest
from . import RestFramework
from .throttling import BaseThrottle

class TestInitApp(BaseFuncTest):
    
    def test_init_app(self):
        # self.app.config.from_pyfile()
        # empty app config
        rf = RestFramework()
        rf.init_app(self.app)
        self.assertIn("extensions", dir(self.app))

    def test_init_throttle_str(self):
        self.app.config["FLASK_RESTFRAMEWORK_THROTTLE_HANDLERS"] = r'[{"class":"flask_restframework.throttling.BaseThrottle","rate":"2/minute"}]'
        rf = RestFramework()
        rf.init_app(self.app)
        self.assertTrue(hasattr(self.app,"THROTTLE_HANDLERS"))
        self.assertEqual(self.app.THROTTLE_HANDLERS, [{"class":BaseThrottle,"rate":"2/minute"}])
    
    def test_init_throttle_obj(self):
        self.app.config["FLASK_RESTFRAMEWORK_THROTTLE_HANDLERS"] = [{"class":BaseThrottle,"rate":"2/minute"}]
        rf = RestFramework()
        rf.init_app(self.app)
        self.assertTrue(hasattr(self.app,"THROTTLE_HANDLERS"))
        self.assertEqual(self.app.THROTTLE_HANDLERS, [{"class":BaseThrottle,"rate":"2/minute"}])