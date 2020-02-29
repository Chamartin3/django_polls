from django.db import models
import json 
import datetime
from termcolor import cprint


class DictionaryField(models.TextField):
    description = "A dictionary stored as text"
    def __init__(self, *args, **kwargs):
        kwargs['default'] = None
        kwargs['null'] = True
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        if isinstance(value, str):
            return json.loads(value)
        if isinstance(value, dict):
            return value


    def to_python(self, value):
        if isinstance(value, str):
            return json.loads(value)
        if isinstance(value, dict) or value is None:
            return value
        raise Exception

    def get_prep_value(self, value):
        if  isinstance(value, dict):
            value = json.dumps(value)
        # import pdb; pdb.set_trace()
        return value



class DurationinYearsField(models.DurationField):
    def to_python(self, value):
        value = super(DurationinYearsField, self).to_python(value)
        if value is None:
            return value

        if isinstance(value, datetime.timedelta):
            return value.days/365,25
        
    
