import base64
import jwt
from .base_test import BaseFuncTest
from . import RestFramework
from .test_throttling import MockCache

class TestViews(BaseFuncTest):
    jwt_secret = "hard_to_guess_secret"

    def test_basic_function(self):
        ''' test basic view '''
        # set up router
        rf = RestFramework()
        rf.init_app(self.app)
        from .views import APIView
        class PingView(APIView):
            def get(self,*args, **kwargs):
                return {"msg":"pong"}
        self.app.add_url_rule("/api/ping",view_func=PingView.as_view('ping'))
        # test
        response = self.client.get('/api/ping')
        # import pdb; pdb.set_trace()
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data.get('msg'),"pong")

    def test_authentication_function(self):
        ''' test view with authentication'''
        # set up router
        rf = RestFramework()
        rf.init_app(self.app)
        from .views import APIView
        from .authentication import BasicAuthentication, JWTAuthentication
        from .permissions import AllowAny, IsAuthenticated
        class PingView(APIView):
            authentication_classes = [BasicAuthentication, JWTAuthentication]
            permission_classes = [AllowAny]
            def get(self,*args, **kwargs):
                return {"msg":"pong"}
        self.app.add_url_rule("/api/ping",view_func=PingView.as_view('ping'))

        # test empty authorization token
        response = self.client.get('/api/ping')
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data.get('msg'),"pong")

        # test wrong base64 auth token
        response = self.client.get('/api/ping',headers={"Authorization":"basic wrong_base64_auth_token"})
        self.assertEqual(response.status_code,401)

        # test wrong jwt auth token
        self.app.config["JWT_SECRET"] = self.jwt_secret
        response = self.client.get('/api/ping',headers={"Authorization":"bearer wrong_jwt_auth_token"})
        self.assertEqual(response.status_code,401)

    def test_permission_function(self):
        ''' test view with permission'''
        # set up router
        rf = RestFramework()
        rf.init_app(self.app)
        from .views import APIView
        from .authentication import BasicAuthentication, JWTAuthentication
        from .permissions import AllowAny, IsAuthenticated
        class PingView(APIView):
            authentication_classes = [BasicAuthentication, JWTAuthentication]
            permission_classes = [IsAuthenticated]
            def get(self,*args, **kwargs):
                return {"msg":"pong"}
        self.app.add_url_rule("/api/ping",view_func=PingView.as_view('ping'))

        # test empty authorization token
        response = self.client.get('/api/ping')
        self.assertEqual(response.status_code,401)
        
        # test base64 auth token
        token = base64.b64encode(b"waro163:passwd123").decode('utf-8')
        response = self.client.get('/api/ping',headers={"Authorization":"basic "+token})
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data.get('msg'),"pong")

        # test jwt auth token
        self.app.config['JWT_SECRET'] = self.jwt_secret
        token = jwt.encode({"id": "1234abcd","iss":"test"}, self.jwt_secret, algorithm="HS256")
        response = self.client.get('/api/ping',headers={"Authorization":"bearer "+token})
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data.get('msg'),"pong")

    def test_anon_throttling_function(self):
        ''' test view with anon throttling'''
        # set up router
        cache = MockCache()
        rf = RestFramework()
        rf.init_app(self.app,cache)
        from .views import APIView
        from .authentication import BasicAuthentication, JWTAuthentication
        from .permissions import AllowAny, IsAuthenticated
        from .throttling import AnonRateThrottle
        class PingView(APIView):
            authentication_classes = [BasicAuthentication, JWTAuthentication]
            permission_classes = [AllowAny]
            throttle_handlers = [{"class":AnonRateThrottle,"rate":"1/minute"}]
            def get(self,*args, **kwargs):
                return {"msg":"pong"}
        self.app.add_url_rule("/api/ping",view_func=PingView.as_view('ping'))

        # test throttling for anon user
        response = self.client.get('/api/ping')
        self.assertEqual(response.status_code,200)
        response = self.client.get('/api/ping')
        self.assertEqual(response.status_code, 429)

        # test throttling for auth user
        token = base64.b64encode(b"waro163:passwd123").decode('utf-8')
        for i in range(5):
            response = self.client.get('/api/ping',headers={"Authorization":"basic "+token})
            self.assertEqual(response.status_code,200)

    def test_user_throttling_function(self):
        ''' test view with user throttling'''
        # set up router
        cache = MockCache()
        rf = RestFramework()
        rf.init_app(self.app,cache)
        from .views import APIView
        from .authentication import BasicAuthentication, JWTAuthentication
        from .permissions import AllowAny, IsAuthenticated
        from .throttling import UserRateThrottle
        class PingView(APIView):
            authentication_classes = [BasicAuthentication, JWTAuthentication]
            permission_classes = [AllowAny]
            throttle_handlers = [{"class":UserRateThrottle,"rate":"1/minute"}]
            def get(self,*args, **kwargs):
                return {"msg":"pong"}
        self.app.add_url_rule("/api/ping",view_func=PingView.as_view('ping'))
        
        # test throttling for anon user
        response = self.client.get('/api/ping')
        self.assertEqual(response.status_code,200)
        response = self.client.get('/api/ping')
        self.assertEqual(response.status_code, 429)

        # test throttling for auth user
        token = base64.b64encode(b"waro163:passwd123").decode('utf-8')
        response = self.client.get('/api/ping',headers={"Authorization":"basic "+token})
        self.assertEqual(response.status_code,200)
        response = self.client.get('/api/ping',headers={"Authorization":"basic "+token})
        self.assertEqual(response.status_code,429)
