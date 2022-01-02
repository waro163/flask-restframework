from flask import g
from unittest import mock
from . import RestFramework
from .base_test import BaseTest
from .throttling import AnonRateThrottle, UserRateThrottle

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
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cache = MockCache()
        rf = RestFramework()
        rf.init_app(cls.app, cache)

    @mock.patch('flask_restframework.throttling.g',current_user=None)
    def test_forbiden(self, *args):
        anon_throttle = AnonRateThrottle("0/s")
        throttle_result = anon_throttle.allow_request()
        self.assertFalse(throttle_result)

    @mock.patch('flask_restframework.throttling.g',current_user=None)
    def test_allow_then_forbiden(self, *args):
        anon_throttle = AnonRateThrottle("1/m")
        # import pdb; pdb.set_trace()
        throttle_result = anon_throttle.allow_request()
        self.assertTrue(throttle_result)
        throttle_result = anon_throttle.allow_request()
        self.assertFalse(throttle_result)
    
    @mock.patch('flask_restframework.throttling.g',current_user=MockUser("1234abcd"))
    def test_allow_for_user(self, *args):
        anon_throttle = AnonRateThrottle("0/s")
        # import pdb; pdb.set_trace()
        throttle_result = anon_throttle.allow_request()
        self.assertTrue(throttle_result)

class TestUserRateThrottle(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cache = MockCache()
        rf = RestFramework()
        rf.init_app(cls.app, cache)

    @mock.patch('flask_restframework.throttling.g',current_user=None)
    def test_forbiden_for_anon_user(self, *args):
        anon_throttle = UserRateThrottle("0/s")
        throttle_result = anon_throttle.allow_request()
        self.assertFalse(throttle_result)

    @mock.patch('flask_restframework.throttling.g',current_user=MockUser("1234abcd"))
    def test_forbiden_for_user(self, *args):
        anon_throttle = UserRateThrottle("0/s")
        throttle_result = anon_throttle.allow_request()
        self.assertFalse(throttle_result)

    @mock.patch('flask_restframework.throttling.g',current_user=MockUser("1234abcd"))
    def test_allow_then_forbiden(self, *args):
        anon_throttle = UserRateThrottle("1/m")
        throttle_result = anon_throttle.allow_request()
        self.assertTrue(throttle_result)
        throttle_result = anon_throttle.allow_request()
        self.assertFalse(throttle_result)