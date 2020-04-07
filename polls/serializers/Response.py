from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from cic_network.cicn_polls.models import Response

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields =('id','responded_at','result', 'participant',
            'poll','question','text','rate'
        )
        extra_kwargs = {
            'text': {'write_only': True, 'required':False},
            'rate': {'write_only': True, 'required':False}
        }
