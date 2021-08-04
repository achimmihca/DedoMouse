from typing import Any, Dict
import jsonpickle # type: ignore
from Config import Config
from ReactiveProperty import ReactiveProperty

class ConfigJsonHandler(jsonpickle.handlers.BaseHandler):
    # 'obj' is the Config object
    def flatten(self, obj: Config, data: Dict[Any, Any]) -> Dict[Any, Any]:
        for k,v in obj.__dict__.items():
            if (isinstance(v, ReactiveProperty)):
                data[k] = self.context.flatten(v.value)
            else:
                data[k] = self.context.flatten(v)
        return data

    # 'obj' is the dictionary with loaded values
    def restore(self, obj: Dict[Any, Any]) -> Config:
        config = Config()
        for k,v in config.__dict__.items():
            if (k in obj):
                loaded_value = self.context.restore(obj[k], reset=False)
                if (isinstance(v, ReactiveProperty)):
                    config.__dict__[k] = ReactiveProperty(loaded_value)
                else:
                    config.__dict__[k] = loaded_value
        return config