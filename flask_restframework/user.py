class BaseUser:
    def __init__(self, id, **kwargs) -> None:
        self._id = id
    
    @property
    def id(self):
        return self._id

    @property
    def is_authenticated(self):
        return True