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




# # class DurationField(Field):
#     """
#     Store timedelta objects.
#     Use interval on PostgreSQL, INTERVAL DAY TO SECOND on Oracle, and bigint
#     of microseconds on other databases.
#     """
#     empty_strings_allowed = False
#     default_error_messages = {
#         'invalid': _('“%(value)s” value has an invalid format. It must be in '
#                      '[DD] [[HH:]MM:]ss[.uuuuuu] format.')
#     }
#     description = _("Duration")

#     def get_internal_type(self):
#         return "DurationField"

#     def to_python(self, value):
#         if value is None:
#             return value
#         if isinstance(value, datetime.timedelta):
#             return value
#         try:
#             parsed = parse_duration(value)
#         except ValueError:
#             pass
#         else:
#             if parsed is not None:
#                 return parsed

#         raise exceptions.ValidationError(
#             self.error_messages['invalid'],
#             code='invalid',
#             params={'value': value},
#         )

#     def get_db_prep_value(self, value, connection, prepared=False):
#         if connection.features.has_native_duration_field:
#             return value
#         if value is None:
#             return None
#         return (24 * 60 * 60 * value.days + value.seconds) * 1000000 + value.microseconds
    
#     def get_db_converters(self, connection):
#         converters = []
#         if not connection.features.has_native_duration_field:
#             converters.append(connection.ops.convert_durationfield_value)
#         return converters + super().get_db_converters(connection)

#     def value_to_string(self, obj):
#         val = self.value_from_object(obj)
#         return '' if val is None else duration_string(val)

#     def formfield(self, **kwargs):
#         return super().formfield(**{
#             'form_class': forms.DurationField,
#             **kwargs,
#         })

class DurationinYearsField(models.DurationField):
    def to_python(self, value):
        value = super(DurationinYearsField, self).to_python(value)
        if value is None:
            return value
        cprint('Hola', 'red')

        import pdb; pdb.set_trace()
        if isinstance(value, datetime.timedelta):
            return value.days/365,25
        
    
