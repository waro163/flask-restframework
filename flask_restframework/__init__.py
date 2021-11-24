
import importlib
import json
import warnings

EXTENSION_NAME = "flask-restframework"

class RestFramework(object):
    def __init__(self,app=None,cache=None) -> None:
        super().__init__()
        if app:
            self.init_app(app,cache)

    def init_app(self, app, cache=None):

        app.extensions = getattr(app, "extensions", {})

        if cache:
            if not hasattr(cache, "set") or not callable(cache.set):
                raise Exception("cache must has .set(key, value) method")
            if not hasattr(cache, "get") or not callable(cache.get):
                raise Exception("cache must has .get(key) method")
            app.CACHE = cache

        if 'FLASK_RESTFRAMEWORK_USER_CLASS' not in app.config:
            warnings.warn(
                'FLASK_RESTFRAMEWORK_USER_CLASS not set in app.config. '
                'Defaulting FLASK_RESTFRAMEWORK_USER_CLASS is flask_restframework.user.BaseUser'
            )
        app.config.setdefault('FLASK_RESTFRAMEWORK_USER_CLASS', "flask_restframework.user.BaseUser")
        app.config.setdefault('FLASK_RESTFRAMEWORK_AUTHENTICATION_CLASSES', '["flask_restframework.authentication.BasicAuthentication"]')
        app.config.setdefault('FLASK_RESTFRAMEWORK_PERMISSION_CLASSES', '["flask_restframework.permissions.AllowAny"]')
        app.config.setdefault('FLASK_RESTFRAMEWORK_EXCEPTION_HANDLER', 'flask_restframework.exceptions.exception_handler')

        user_class_path = app.config.get("FLASK_RESTFRAMEWORK_USER_CLASS")
        user_cls = import_string(user_class_path)
        app.USER_CLASS = user_cls

        app.AUTHENTICATION_CLASSES = perform_import(app.config.get("FLASK_RESTFRAMEWORK_AUTHENTICATION_CLASSES"))
        app.PERMISSION_CLASSES = perform_import(app.config.get("FLASK_RESTFRAMEWORK_PERMISSION_CLASSES"))
        app.EXCEPTION_HANDLER = import_string(app.config.get("FLASK_RESTFRAMEWORK_EXCEPTION_HANDLER"))
        _throttle_handlers = app.config.get("FLASK_RESTFRAMEWORK_THROTTLE_HANDLERS")
        if _throttle_handlers:
            app.THROTTLE_HANDLERS = perform_throttle_import(_throttle_handlers)
            if not cache:
                warnings.warn("throttle handlers will not work due to not configure cache")

        app.extensions[EXTENSION_NAME] = self

def perform_import(string_name):
    if isinstance(string_name, str):
        try:
            class_list = json.loads(string_name)
        except Exception:
            raise Exception(f"{string_name} string Must be list format: [' ',' ',...]")
    elif isinstance(string_name, (list, tuple)):
        class_list = string_name
    
    return [import_string(item) for item in class_list]

def perform_throttle_import(string_name):
    if isinstance(string_name, str):
        try:
            class_list = json.loads(string_name)
        except Exception:
            raise Exception(string_name+r" string Must be list format: [{'class':'xxx','rate':'xxx/xxx'}',...]")
    elif isinstance(string_name, (list, tuple)):
        class_list = string_name
    
    throttle_handlers = []
    for item in class_list:
        if not isinstance(item, dict):
            raise Exception("throttle_handlers' item must be dict type")
        throttle_handler = {"rate":item.get("rate")}
        item_class = item.get("class")
        if isinstance(item_class, str):
            throttle_class = import_string(item_class)
        else:
            throttle_class = item_class
        throttle_handler.update({"class":throttle_class})
        throttle_handlers.append(throttle_handler)
    return throttle_handlers

def import_string(setting_name):
    try:
        module_path, cls_name = setting_name.rsplit(".", 1)
        cls = getattr(importlib.import_module(module_path), cls_name)
        return cls
    except Exception as e:
        raise Exception(f'{setting_name} import error: {e.__str__()}')
