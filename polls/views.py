# Django
from django.shortcuts import render


# Django Rest Freamework
from rest_framework.response import Response
from rest_framework import viewsets, generics,serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError


# Local
from .procesing.serializing import process_responses
from .models import Poll, Question, Response as PollResponse
from .serializers import (
    PollSerializer,
    QuestionSerializer,
    ResponseSerializer, 
    QuestionResponseSerializer)


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.order_by('-cohort__fecha_inicio')
    serializer_class = PollSerializer

    def create(self, request, *args, **kwargs):
     serializer = self.get_serializer(data=request.data)
     serializer.is_valid(raise_exception=True)
     self.perform_create(serializer)
     headers = self.get_success_headers(serializer.data)
     return Response(serializer.data, status=201, headers=headers)

    @action(detail=True, methods=['post'])
    def respond(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.data.get('participant')
        questions = request.data.get('responses')
        for question, value in questions.items():
            resp = PollResponse.objects.get(question_id=question,
                participant_id=user,
                poll=instance)
            
            resp.respond( value=value )
            resp.save()
        # import pdb; pdb.set_trace()
        return Response({'message':"Gracias por responder la encuesta"})



class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

 

    @action(detail=True, methods=['post'])
    def results(self, request, pk=None):
        '''Revuelve los resultados de la pregunta'''
        question = self.get_object()
        poll = request.data.pop('poll', None)
        serializer = QuestionResponseSerializer(question, poll=poll)
        # serializer.is_valid()
        return Response(serializer.data, status=201)



class ResponseViewSet(viewsets.ModelViewSet):
    queryset = PollResponse.objects.all()
    serializer_class = ResponseSerializer

    def create(self, request):
        responses = self.request.data.get('responses', None)
        if responses is None:
            return Response(data="{'message':'No hay datos.'}", status=400)

        valid_responses=[]
        for response in responses:
            sresp = ResponseSerializer(data=response)
            try:
                sresp.is_valid(raise_exception=True)
            except ValidationError as e:
                if e.detail['non_field_errors'][0].code=='unique':
                    return Response(data={'message':'La respuesta de este usuario ya fue registrada'}, status=400)

            valid_responses.append(sresp)

        data=[]
        for response in valid_responses:
            response.save()
            data.append(response.data)

        message={
        'message':'Respuestas Registradas con Exito',
        'data':data,
        }
        return Response(data=message, status=201)

