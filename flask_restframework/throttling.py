
class BaseThrottle:
    """
    Rate throttling of requests.
    """
    def __init__(self, rate:str):
        self.rate = rate

    def allow_request(self):
        """
        Return `True` if the request should be allowed, `False` otherwise.
        """
        raise NotImplementedError('.allow_request() must be overridden')
    
    def parse_rate(self):
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

    def throttle_success(self):
        return True

    def throttle_failure(self):
        """
        Called when a request to the API has failed due to throttling.
        """
        return False