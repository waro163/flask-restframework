from .base_test import BaseTest
from unittest import mock
from .authentication import BasicAuthentication, JWTAuthentication
from .exceptions import AuthenticationFailed
from . import RestFramework
import base64
from flask import g

class TestBasicAuthentication(BaseTest):

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
            # import pdb; pdb.set_trace()
            basic_auth.authenticate()
        except Exception as e:
            self.assertIsInstance(e,AuthenticationFailed)
            self.assertIn("not correctly base64 encoded", e.__str__())

    @mock.patch("flask_restframework.authentication.request",headers={"Authorization":"basic "+base64.b64encode(b"waro163:passwd123").decode('utf-8')})
    def test_base64_token(self, *args):
        rf = RestFramework()
        rf.init_app(self.app)
        basic_auth = BasicAuthentication()
        basic_auth.authenticate()
        self.assertTrue(hasattr(g,"current_user"))

    
