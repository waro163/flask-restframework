from .base_test import BaseTest,BaseFuncTest
from unittest import mock
from .authentication import BasicAuthentication, JWTAuthentication
from .exceptions import AuthenticationFailed, ConfigureError
from . import RestFramework
import base64
import jwt
from flask import g

class TestBasicAuthentication(BaseFuncTest):

    @mock.patch("flask_restframework.authentication.request",headers={"Authorization":""})
    def test_empty_token(self, *args):
        basic_auth = BasicAuthentication()
        self.assertIsNone(basic_auth.authenticate())

    @mock.patch("flask_restframework.authentication.request",headers={"Authorization":"basic"})
    def test_no_token(self, *args):
        basic_auth = BasicAuthentication()
        try:
            basic_auth.authenticate()
        except Exception as e:
            self.assertIsInstance(e,AuthenticationFailed)

    @mock.patch("flask_restframework.authentication.request",headers={"Authorization":"basic wrong_base64_auth_token"})
    def test_wrong_base64_token(self, *args):
        basic_auth = BasicAuthentication()
        try:
            basic_auth.authenticate()
        except Exception as e:
            self.assertIsInstance(e,AuthenticationFailed)
            self.assertIn("not correctly base64 encoded", e.__str__())

    @mock.patch("flask_restframework.authentication.request")
    def test_base64_token(self, mock_headers):
        user_id = "waro163"
        user_passwd = "passwd123"
        mock_headers.headers = {"Authorization":"basic "+base64.b64encode(b"waro163:passwd123").decode('utf-8')}
        # for init user class
        rf = RestFramework()
        rf.init_app(self.app)
        basic_auth = BasicAuthentication()
        usr,inf = basic_auth.authenticate()
        self.assertTrue(hasattr(g,"current_user"))
        self.assertEqual(usr.id, user_id)
        self.assertEqual(inf.get('id'), user_id)
        self.assertEqual(inf.get('password'), user_passwd)


class TestJWTAuthentication(BaseFuncTest):
    jwt_secret = "hard_to_guess_secret"

    @mock.patch("flask_restframework.authentication.request",headers={"Authorization":""})
    def test_empty_token(self, *args):
        jwt_auth = JWTAuthentication()
        self.assertIsNone(jwt_auth.authenticate())

    @mock.patch("flask_restframework.authentication.request",headers={"Authorization":"bearer"})
    def test_no_token(self, *args):
        jwt_auth = JWTAuthentication()
        try:
            jwt_auth.authenticate()
        except Exception as e:
            self.assertIsInstance(e,AuthenticationFailed)

    @mock.patch("flask_restframework.authentication.request",headers={"Authorization":"bearer not_config_jwt_secret"})
    def test_not_config_jwt_secret(self, *args):
        jwt_auth = JWTAuthentication()
        try:
            # import pdb; pdb.set_trace()
            jwt_auth.authenticate()
        except Exception as e:
            self.assertIsInstance(e, ConfigureError)

    @mock.patch("flask_restframework.authentication.request",headers={"Authorization":"bearer wrong_jwt_auth_token"})
    def test_wrong_jwt_token(self, *args):
        self.app.config['JWT_SECRET'] = self.jwt_secret
        jwt_auth = JWTAuthentication()
        try:
            # import pdb; pdb.set_trace()
            jwt_auth.authenticate()
        except Exception as e:
            self.assertIsInstance(e,AuthenticationFailed)

    @mock.patch("flask_restframework.authentication.request")
    def test_exclude_id_jwt_token(self, mock_header):
        self.app.config['JWT_SECRET'] = self.jwt_secret
        token = jwt.encode({"name": "1234abcd","iss":"test"}, self.jwt_secret, algorithm="HS256")
        mock_header.headers = {"Authorization":"bearer "+token}
        jwt_auth = JWTAuthentication()
        try:
            jwt_auth.authenticate()
        except Exception as e:
            self.assertIsInstance(e,AuthenticationFailed)
            self.assertIn("'id' field not found",e.__str__())

    @mock.patch("flask_restframework.authentication.request")
    def test_normal_jwt_token(self, mock_header):
        self.app.config['JWT_SECRET'] = self.jwt_secret
        token = jwt.encode({"id": "1234abcd","iss":"test"}, self.jwt_secret, algorithm="HS256")
        mock_header.headers = {"Authorization":"bearer "+token}
        # for init user class
        rf = RestFramework()
        rf.init_app(self.app)
        jwt_auth = JWTAuthentication()
        jwt_auth.authenticate()
        self.assertTrue(hasattr(g,"current_user"))