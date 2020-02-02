
# Python Modules
import statistics
from datetime import timedelta

# Dajgno Modules
from django.db import models
from django.db.models import F, ExpressionWrapper, fields

# Local Tools
from polls.utils import DurationinYearsField
from polls.serializing  import  frecuency_dist_ages

def compute_age(dic):
    bd = dic['participant__profile__birth_date']
    if not bd:
        return 0
    event_date = dic['poll__cohort__fecha_inicio']
    return  int((event_date - bd).days / 365.25)


class ResponsesQuerySet(models.QuerySet):
    
    def completed(self):
        return self.filter(responded=True)

    def ages(self):
        # import pdb; pdb.set_trace()
        return [r.respondant_age for r in self.all()]

    def age_distribution(self):
        return frecuency_dist_ages(self.ages())
   
    def males(self):
        return self.filter(participant__profile__gender='M')

    def females(self):
        return self.filter(participant__profile__gender='F')

    def rates_by_gender(self):
        # import pdb; pdb.set_trace()
        return {reg['gender']:reg['total'] for reg in self.values('participant__profile__gender').annotate(
                gender=F('participant__profile__gender'),  
                total=models.Avg('rate'))
            }
    
    def rates_by_age(self):
        rates_by_birth =  self.values(
            'participant__profile__birth_date', 
            'poll__cohort__fecha_inicio')\
            .annotate(models.Avg('rate'))
        
        # import pdb; pdb.set_trace()
        
        ages = {}
        for rate in rates_by_birth:
            bd = rate['participant__profile__birth_date']
            if bd:
                event_date = rate['poll__cohort__fecha_inicio']
                age = int((event_date - bd).days / 365.25)
            else:
                age = 0

            if ages.get(age,None):
                ages[age].append(rate['rate__avg'])
            else:
                ages[age] = [rate['rate__avg']]
        
  
        avg_ages = {}
        for age,rates in ages.items():
            if len(rates) > 0:
                avg_ages[age] = statistics.mean(rates) 
            else:
                avg_ages[age] = 0
        return avg_ages

    def rates_by_age_dist(self):
        distribution = self.age_distribution()
        rates_by_age = self.rates_by_age()
        distributed = {}
        for point in distribution:
            point_rates = [r for age,r in rates_by_age.items() if point['min'] <= age <= point['max'] ]
            if len(point_rates):
                distributed[point['name']] =  statistics.mean(point_rates)
            else:
                distributed[point['name']] =  0
        return distributed 

    def rate_avg(self):
        rateAvg = self.aggregate(rate=models.Avg('rate'), respuestas=models.Count('rate'))
        return { k:v if v else 0 for k,v in rateAvg.items() }

    def response_word_count(self):
        counts = [k.processed_response for k in self.all() if k.processed_response is not None]
        wc = {}
        for dic in counts:
            for word, count in dic.items():
                if wc.get(word,None):
                    wc[word]= wc[word] + count
                else:
                    wc[word] = count
        return wc

    def distributed_by_age(self):
        diference = ExpressionWrapper(
            F('poll__cohort__fecha_inicio') - F('participant__profile__birth_date'),
            output_field=fields.DurationField())
        
        age_diff_qs= self.annotate(age_dist=diference)
        distribution = self.age_distribution()
        for dist_range in distribution:
            initial_age = timedelta(days=365.25 *  dist_range['min'])
            final_age = timedelta(days=365.25 *  dist_range['max'])
            dist_range['qs'] = age_diff_qs.filter(
                age_dist__range=(initial_age, final_age))
        distribution.append({
            'name':'no age',
            'min':0,
            'max':0,
            'qs': age_diff_qs.filter(age_dist=None)
        })
        
        return distribution


    def total_by_gender(self):
        return self.values('participant__profile__gender') \
        .annotate(
            gender=models.F('participant__profile__gender'), 
            total=models.Count('participant__profile__gender'))

    def total_by_age_dist(self):
        age_dist = self.distributed_by_age()
        ranges = {}
        for age_range in age_dist:
            ranges[age_range[ 'name' ] ]=  age_range[ 'qs' ].count()
        return ranges


    def sumary(self):
        rates = self.values('responded').annotate(
                field = models.F('responded'),
                count=models.Count('responded'))

        total = 0
        to_respond = 0
        reponded = 0
        for rate in rates:
            if rate['field']:
                reponded = rate['count'] 
            if not rate['field']:
                to_respond = rate['count'] 
            total = total + rate['count']
        
        perc = 0
        if reponded > 0:
            perc = reponded / total


        return {
            'responded': reponded,
            'to_respond': to_respond,
            'percentage': perc,
            'expected': total
        }

    
class ResponseManager(models.Manager):
    # use_for_related_fields = True
    def get_queryset(self):
        return ResponsesQuerySet(self.model, using=self._db)
    
