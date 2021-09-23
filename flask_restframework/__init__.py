
import importlib
import json
import warnings

EXTENSION_NAME = "flask-restframework"

class RestFramework(object):
    def __init__(self,app=None) -> None:
        super().__init__()
        if app:
            self.init_app(app)

    def init_app(self, app):

        app.extensions = getattr(app, "extensions", {})

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
    

def import_string(setting_name):
    try:
        module_path, cls_name = setting_name.rsplit(".", 1)
        cls = getattr(importlib.import_module(module_path), cls_name)
        return cls
    except Exception as e:
        raise Exception(f'{setting_name} import error: {e.__str__()}')
