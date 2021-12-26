from flask import current_app, request, g
import time

class BaseThrottle:
    """
    Rate throttling of requests.
    """
    cache_format = 'throttle_%(scope)s_%(ident)s'
    now = time.time()

    def __init__(self, rate:str):
        self.rate = rate
        self.num_requests, self.duration = self.parse_rate(self.rate)
        self.cache = getattr(current_app, "CACHE", None)

    def allow_request(self):
        """
        Return `True` if the request should be allowed, `False` otherwise.
        """
        if self.cache is None:
            return True
        if self.rate is None:
            return True

        self.key = self.get_cache_key()
        if self.key is None:
            return True

        self.history = self.cache.get(self.key) or []
        #  Drop any requests from the history which have now passed the throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()

    def get_cache_key(self):
        """
        Should return a unique cache-key which can be used for throttling.
        Must be overridden.

        May return `None` if the request should not be throttled.
        """
        raise NotImplementedError('.get_cache_key() must be overridden')

    def parse_rate(self,rate):
        """
        Given the request rate string, return a two tuple of:
        <allowed number of requests>, <period of time in seconds>
        """
        if self.rate is None:
            return (None, None)
        num, period = self.rate.split('/')
        num_requests = int(num)
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        return (num_requests, duration)

    def get_ident(self):
        return request.remote_addr

    def throttle_success(self):
        """
        Inserts the current request's timestamp along with the key
        into the cache. key's expire time(ttl) is duration
        """
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)
        return True

    def throttle_failure(self):
        """
        Called when a request to the API has failed due to throttling.
        """
        return False
    
    def wait(self):
        """
        Returns the recommended next request time in seconds.
        """
        if self.history:
            remaining_duration = self.duration - (self.now - self.history[-1])
        else:
            remaining_duration = self.duration

        available_requests = self.num_requests - len(self.history) + 1
        if available_requests <= 0:
            return None

        return remaining_duration / float(available_requests)

class AnonRateThrottle(BaseThrottle):
    """
    Limits the rate of API calls that may be made by a anonymous users.

    The IP address of the request will be used as the unique cache key.
    """
    scope = 'anon'

    def get_cache_key(self):
        if g.current_user and g.current_user.is_authenticated:
            return None # Only throttle unauthenticated requests.

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident()
        }

class UserRateThrottle(BaseThrottle):
    """
    Limits the rate of API calls that may be made by a given user.

    The user id will be used as a unique cache key if the user is
    authenticated.  For anonymous requests, the IP address of the request will
    be used.
    """
    scope = 'user'

    def get_cache_key(self):
        if g.current_user and g.current_user.is_authenticated:
            ident = g.current_user.id
        else:
            ident = self.get_ident()

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }