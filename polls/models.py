from django.db import models

# Create your models here.
from django.db import models
from cic_network.cicn_courses.models import Cohort, Teacher, Participant
from cic_network.cicn_users.models import User
import functools
import statistics
from cic_network.utils import DictionaryField
from cic_network.cicn_polls.procesing.nlp import Processor

from .managers import ResponseManager

from cic_network.cicn_polls.procesing.serializing import (
    calculateAge, 
    frecuency_dist, 
    frecuency_dist_ages as frecuency_dist_respnses, 
    process_responses,
    distributed_responses
    )





class Response(models.Model):
    poll = models.ForeignKey('Poll',
        on_delete=models.CASCADE,
        related_name='responses')

    question = models.ForeignKey('Question',
        on_delete=models.CASCADE,
        related_name='responses')

    participant = models.ForeignKey(User,
        null=True,
        on_delete=models.CASCADE,
        related_name='responses')

    responded_at = models.DateTimeField(auto_now=True)
    responded = models.BooleanField(default=False, blank=True)
    text = models.CharField(blank=True, null=True, max_length=100)
    rate = models.PositiveIntegerField(blank=True, null=True)
    processed_response = DictionaryField(default=None)


    class Meta:
        verbose_name = "Response"
        verbose_name_plural = "Responses"
        unique_together = ['poll', 'question','participant']
    
    objects = ResponseManager()

    def __str__(self):
        if self.result:
            return self.result
        return ''
    
    def respond(self, value):
        if self.question.type=='2':
            self.rate=value
        else:
            self.text = value
        self.responded = True

    

    @property
    def respondant_age(self):
        bd = self.participant.profile.birth_date
        if not bd:
            return 0
        event_date = self.poll.cohort.fecha_inicio
        # import pdb; pdb.set_trace()
        return  int((event_date - bd).days / 365.25)


    @property
    def result(self):

        if not self.responded:
            return None
        res = self.rate if self.question.type=='2' else self.text
        return f'{res}'
    
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.question.type == '1' and self.text is not None:
            self.responded = True
            pros = Processor()
            self.processed_response = pros.process(self.text)

        if self.question.type == '2' and self.rate is not None:
            self.responded = True
        
        return super(Response, self).save(*args, **kwargs)


class Question(models.Model):
    RESP_TYPES = ((1,'text'),(2,'rate'))
    type = models.CharField(max_length=100, choices=RESP_TYPES)
    text = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        

    def __str__(self):
        return f'{self.text}'

    # def age_dist(self):
    #     rby = self.responded_by()
    #     return frecuency_dist(rby, self.cohort.fecha_inicio)


    def responded_by(self, poll=None):
        responded = []
        for resp in self.responses.all():
            # import pdb;pdb.set_trace()

            if poll is not None:
                if resp.poll.id == poll:
                    responded.append(resp.participant)
            else:
                responded.append(resp.participant)
        return responded
    
    

    def distributed_responses(self,responses):
        return distributed_responses(responses)

    def is_responded(self, poll_id=None):
        mising = self.mising_responses(poll_id)
        if mising:
            return False
        return True 

    def procesed_responses(self, poll=None):
        responses = self.spec_responses(poll)

        if self.type == '1':
            return responses.response_word_count()
        else:
            return {
            'total': responses.count(),
            'gender': responses.rates_by_gender(),
            'age': responses.rates_by_age_dist(),
            'average': responses.rate_avg()
            }

    def spec_responses(self, poll=None):
        responses = self.responses.filter(responded=True)
        if poll:
            responses = responses.filter(poll__id=poll)
        return responses
        
    def mising_responses(self, poll_id=None):
        qs = self.responses
        if poll_id:
            qs = qs.filter(poll__id=poll_id)
        return [res.responded for res in qs.all() if res.responded == False ]


class Poll(models.Model):
    name = models.CharField(
        max_length=100, 
        default="", blank=True)
    cohort = models.ForeignKey(Cohort, 
        on_delete=models.CASCADE, 
        related_name='polls')
    teachers = models.ManyToManyField(Teacher)
    questions = models.ManyToManyField('Question', 
        related_name="polls")

    participants = models.ManyToManyField('cicn_users.User', 
        related_name='polls', 
        through='Response')

    open = models.BooleanField(default=True, blank=True)


    class Meta:
        verbose_name = "Poll"
        verbose_name_plural = "Polls"


    def __str__(self):
        return f'{self.cohort.name}'

    # def save(self, *args, **kwargs):
    #     import pdb; pdb.set_trace()
    #     super(Poll, self).save(*args, **kwargs)
    #     self.create_empty_responses()

    def close(self):
        self.open = False
        self._empty_responses.delete()

    @property
    def _empty_responses(self):
        return self.responses.filter(responded=True)


    @property
    def expected_respondants(self):
        return [p.user for p in self.cohort.participant.all() ]

    def mising_response(self):
        return [i for i in self.expected_respondants  if i not in self.all_respondants]

    @property
    def all_respondants(self):
        '''
            Every user that is asigned to response 
        
        '''
        return list({u.participant for u in self.responses.all()})

    def create_empty_responses(self):
        # import pdb; import pdb; pdb.set_trace()
        return Response.objects.bulk_create(self._get_empty_responses())

    def _get_empty_responses(self):
        '''
            Empty responses based on users related to the cohort
        '''
        res_batch = []
        for expected in self.mising_response():
            for q in self.questions.all():
                res_batch.append(Response(
                    poll=self, 
                    question=q, 
                    participant=expected))
        return res_batch

    
    @property
    def resposes_sumary(self):
        return self.responses.all().sumary()

    @property
    def respondants(self):
        '''
            Gente que ya respondió todas las preguntas
        '''
        return list({u.participant for u in self.responses.filter(responded=True).all()})
        
    def participant_complete(self, part):
        return part in self.respondants


    @property
    def completed(self):
        return all([q.is_responded(self.id) for q in self.questions.all()])

    def audience(self):
        user_qs = User.objects.filter(id__in=[r.id for r in self.respondants])
        return {
            'gender':user_qs.gender_dist(),
            'nationality':user_qs.nac_dist(),
            'age':user_qs.total_by_age_dist(self.cohort.fecha_inicio)
        }
   