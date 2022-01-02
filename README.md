# Installation

    pip install flask-rest-framework

# Test

    py.test .

# Overview
flask-rest-framework is inspired by [Django REST framework](https://github.com/encode/django-rest-framework)

You can use this extension to develop your rest api quickly based on flask, each view contains this:

* Authentication policies
* Permission
* Throttle

and each of them can be customized yourself, all of those are revolved around `User`, so you can define your own
User class.

# Example

```python
from flask import Flask,jsonify
from flask_restframework import RestFramework

app = Flask(__name__)
rf = RestFramework()
rf.init_app(app)

from flask_restframework.views import APIView
from flask_restframework.authentication import BasicAuthentication,JWTAuthentication
from flask_restframework.permissions import AllowAny,IsAuthenticated

class PingView(APIView):

    authentication_classes=[BasicAuthentication, JWTAuthentication]
    permission_classes=[IsAuthenticated,]
    
    def get(self, *args, **kwargs):
        return jsonify({"args":args,"kwargs":kwargs,"request.args":request.args})

app.add_url_rule("/ping/<string:name>",view_func=PingView.as_view('ping'))

if __name__ == "__main__":
    app.run()
```

# User

if you define your own `User` class, must configure it in flask config env: `FLASK_RESTFRAMEWORK_USER_CLASS`

```python
app.config['FLASK_RESTFRAMEWORK_USER_CLASS] = 'your_user_class_path.YourUser'
```

and `User` class must has `is_authenticated` attribute, the type is boolean, this attribute will be used in permission.

more detail can see `flask_restframework.user.BaseUser`, i recomend your class inherit from it.

we use the `User` in authentication

# Authenticaion

we offer `BasicAuthentication` and `JWTAuthentication` authentication class here, you could custom your authentication class or inherit them to complete auth

# Permission

`AllowAny` permission class allows anyone access your API without authentication;

`IsAuthenticated` user must be authenticated before accessing API;

`IsAuthenticatedOrReadOnly` allow anyone access API if request method is safe('get','head','options'), else must be authenticated.

# Throttling

before using throttle, we must configure cache to app, else it will not work:
```
from xxx import Cache
...
app = Flask(__name__)
cache = Cache()
rf = RestFramework()
rf.init_app(app,cache)
...
```
here we offer `AnonRateThrottle` and `UserRateThrottle`.

and the rate of throttling can be set by `second`,`minute`,`hour`,`day`.

```
...
class YourView(APIView):
    authentication_classes=[BasicAuthentication, JWTAuthentication]
    throttle_handlers = [{"class":AnonRateThrottle,"rate":"1/hour"},{"class":UserRateThrottle,"rate":"10/minute"}]
...
```

### AnonRateThrottle

the `AnonRateThrottle` is for throttling anonymous user, namely permission class is `AllowAny`, if user is authenticated, it will not limit.

### UserRateThrottle

the `UserRateThrottle` is for throttling authenticated user, if user is not authenticated, it also work.
