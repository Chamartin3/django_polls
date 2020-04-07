
from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from cic_network.cicn_polls.models import Question, Poll
from rest_framework.exceptions import ValidationError
from cic_network.cicn_courses.serializers import (
                                        TeacherSerializer,
                                        SimpleParticipantSerializer,
                                        SimpleCohortSerializer,
                                        ParticipantSerializer)


class QuestionSerializer(serializers.ModelSerializer):
    model = Question
    fields : '__all__'


class FastQuestionSerializer(WritableNestedModelSerializer):

    class Meta:
        model = Question
        fields = (
            'id',
            'text',
            'type',)

class FastPollSerializer(serializers.ModelSerializer):
    cohort = SimpleCohortSerializer(
        read_only=True,
        required=False)
    teachers = TeacherSerializer(
        read_only=True,
        many=True,
        required=False)
    questions_info = FastQuestionSerializer(
        source="questions",
        read_only=True,
        many=True,
        required=False)


    class Meta:
        model = Poll
        fields = [
            'id',
            'cohort',
            'name',
            'teachers',
            'questions_info',
            'questions',
            ]

class PollSerializer(serializers.ModelSerializer):
    questions_info = FastQuestionSerializer(
        source="questions",
        read_only=True,
        many=True,
        required=False)

    teachers_info = TeacherSerializer(
        read_only=True,
        many=True,
        source='teachers',
        required=False)


    context = serializers.SerializerMethodField()
    audience = serializers.SerializerMethodField()
    class Meta:
        model = Poll
        fields = [
            'id',
            'cohort',
            'name',
            'teachers',
            'teachers_info',
            'questions',
            'questions_info',
            'context',
            'resposes_sumary',
            'audience',
        ]

    def get_audience(self, poll):
        return poll.audience()

    def get_context(self, poll):
        return {
            'id':poll.cohort.id,
            'name':poll.cohort.name
        }
    
    def create(self, validated_data):
        # questions = self.validated_data.pop('questions')
        # qobjs = []
        # for quest in questions:
        #     qobjs.append(Question.objects.get(pk=quest))
    
        # if not questions or  len(questions) === 0:
        #     ValidationError('Le encuesta tiene que tener por lo menos una pregunta')
        # poll = Poll(**validated_data)
        # poll.save()
        # import pdb; pdb.set_trace()

        poll = super(PollSerializer, self).create(validated_data)
        poll.create_empty_responses()
        return poll


    # def create(self, validated_data):
    #     import pdb; pdb.set_trace()


# class PollDetailSerializer(serializers.ModelSerializer):
#     questions_info = FastQuestionSerializer(
#         source="questions",
#         read_only=True,
#         many=True,
#         required=False)

#     teachers = TeacherSerializer(
#     read_only=True,
#     many=True,
#     required=False)

#     gender_gap = serializers.SerializerMethodField()
#     age_dist = serializers.SerializerMethodField()

#     class Meta:
#         model = Poll
#         fields = [
#             'id',
#             'cohort',
#             'name',
#             'teachers',
#             'expected_responses',
#             'total_responses',
#             'responds_percentage',
#             # 'to_response',
#             # 'respondants',
#             'questions_info',
#             'questions',
#             'gender_gap',
#             'age_dist'
#         ]

#     def get_gender_gap(self, obj):
#         return obj.get_genders()

#     def get_age_dist(self, obj):
#         return obj.age_dist()
