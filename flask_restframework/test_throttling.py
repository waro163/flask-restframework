from flask import g
from unittest import mock
from . import RestFramework
from .base_test import BaseTest
from .throttling import AnonRateThrottle

class MockCache:
    def __init__(self) -> None:
        self.data = {}

    def set(self, key, value, timeout=None):
        self.data.update({key:value})

    def get(self, key):
        return self.data.get(key)

class MockUser:
    def __init__(self,id) -> None:
        self.id = id
        self.is_authenticated = True

class TestAnonRateThrottle(BaseTest):

    # @mock.patch('flask_restframework.throttling.g',current_user=None)
    def test_forbiden(self, *args):
        cache = MockCache()
        rf = RestFramework()
        rf.init_app(self.app, cache)
        anon_throttle = AnonRateThrottle("0/s")
        throttle_result = anon_throttle.allow_request()
        self.assertFalse(throttle_result)

    def test_allow_then_forbiden(self, *args):
        cache = MockCache()
        rf = RestFramework()
        rf.init_app(self.app, cache)
        anon_throttle = AnonRateThrottle("1/m")
        # import pdb; pdb.set_trace()
        throttle_result = anon_throttle.allow_request()
        self.assertTrue(throttle_result)
        throttle_result = anon_throttle.allow_request()
        self.assertFalse(throttle_result)
    
    @mock.patch('flask_restframework.throttling.g',current_user=MockUser("1234abcd"))
    def test_allow_for_user(self, *args):
        cache = MockCache()
        rf = RestFramework()
        rf.init_app(self.app, cache)
        anon_throttle = AnonRateThrottle("0/s")
        # import pdb; pdb.set_trace()
        throttle_result = anon_throttle.allow_request()
        self.assertTrue(throttle_result)