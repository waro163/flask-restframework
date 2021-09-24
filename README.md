## Installation 

    pip install flask-rest-framework

# Overview
flask-rest-framework is inspired by [Django REST framework](https://github.com/encode/django-rest-framework)

You can use this extension to develop your rest api quickly based on flask, each view contains this:

* Authentication policies
* Permission
* Throttle(todo)

and each of them can be customized yourself, all of those are revolved around `User`, so you can difine your own
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

## test

    py.test .