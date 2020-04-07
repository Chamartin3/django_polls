
from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from cic_network.cicn_polls.models import Question, Poll
from .Response import  ResponseSerializer

from cic_network.cicn_polls.procesing.serializing import process_responses


class QuestionSerializer(serializers.ModelSerializer):
    # responses = ResponseSerializer(many=True, required=False)
    polls = serializers.SerializerMethodField()
    responses = serializers.SerializerMethodField()
    efective_responses = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = (
            'id',
            'text',
            'type',
            'polls',
            'responses',
            'efective_responses',
            )
        

    def get_polls(self, question):
        return question.polls.count()    
    
    def get_responses(self, question):
        return question.responses.count()
    
    def get_efective_responses(self, question):
        return question.responses.filter(responded=True).count()



class QuestionResponseSerializer(serializers.ModelSerializer):
    responses = serializers.SerializerMethodField()
    processed = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = (
            'id',
            'text',
            'type',
            'polls',
            'processed',
            'responses'
            )
    def __init__(self, *args, **kwargs):
        self.poll = kwargs.pop('poll', None)
        super(QuestionResponseSerializer, self).__init__(*args, **kwargs)

    def get_processed(self, question):
        return question.procesed_responses(self.poll)

    def get_responses(self, question):
        responses = question.spec_responses(self.poll)
        return [response.result for response in responses ]



