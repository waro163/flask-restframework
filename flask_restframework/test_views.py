from .base_test import BaseTest,BaseFuncTest
from . import RestFramework

class TestView(BaseTest):

    def test_view_no_init(self):
        from .views import APIView
        view = APIView()
        self.assertIn("authentication_classes", dir(view))
        self.assertEquals([], view.authentication_classes)

    # def test_view_after_init(self):
    #     rf = RestFramework()
    #     rf.init_app(self.app)
    #     from .views import APIView
    #     from .authentication import BasicAuthentication
    #     class MyView(APIView):
    #         authentication_classes = [BasicAuthentication,]
    #     view = MyView()
    #     self.assertIn("authentication_classes", dir(view))
    #     self.assertNotEqual([],view.authentication_classes)

