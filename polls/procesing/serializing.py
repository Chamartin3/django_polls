from .nlp import Processor
import functools
import statistics


def calculateAge(birthDate, ws_date= None):
    if birthDate is None:
        return None
    today = ws_date if ws_date is not None else date.today()
    age = today.year - birthDate.year - ((today.month, today.day) <
         (birthDate.month, birthDate.day))

    return age

def frecuency_dist(participants):
    ages = [p.age_in_event for p in participants if p.age_in_event is not None ]
    if len(ages)==0:
        return {'min':0, 'max': 0, 'dist':{}, 'dist_avg':{}}

    maximun = max(ages)
    minimum = min(ages)
    rang = maximun - minimum
    k_inter = 5 if len(ages) > 5 else len(ages)
    a_mplitud = round(rang / k_inter)
    distribution = {
    'min':minimum,
    'max': maximun,
    'dist':{},
    'dist_total':{},
    'dist_avg':{},
    }

    if k_inter==1:
        k = f'{minimum}'
        distribution['dist'][k]= [minimum]
        distribution['dist_total'][k]= 1
        distribution['dist_avg'][k] =minimum
    else:
        for n in range(1,k_inter+1):
            mininterval = minimum if n == 1 else mininterval + a_mplitud+1
            maxinterval = mininterval + a_mplitud
            k = f'{mininterval}-{maxinterval}'
            data = [x for x in ages if  mininterval <= x <= maxinterval]
            distribution['dist'][k]= data
            distribution['dist_total'][k]= len(data)
            distribution['dist_avg'][k] =  statistics.mean(data) if len(data) > 0 else 0


    return distribution

def frecuency_dist_ages(ages):

    ages=[x for x in ages if x is not None]

    if len(ages)==0:
        return [{'name':'unico','min':0, 'max': 0, 'dist':{}, 'dist_avg':{}}]

    #
    # import pdb;pdb.set_trace()
    maximun = max(ages)
    minimum = min(ages)
    rang = maximun - minimum
    k_inter = 5 if len(ages) > 5 else len(ages)
    a_mplitud = round(rang / k_inter)
    distribution = []

    if k_inter==1:
        k = f'{minimum}'
        point={}
        point['name'] = k
        point['min'] = minimum
        point['max' ]= maximun
        distribution.append(point)
    else:

        for n in range(1,k_inter+1):
            mininterval = minimum if n == 1 else mininterval + a_mplitud+1
            maxinterval = mininterval + a_mplitud
            k = f'{mininterval}-{maxinterval}'
            point={}
            point['name'] = k
            point['min'] = mininterval
            point['max' ]= maxinterval
            distribution.append(point)

    return distribution


def process_responses(tipo, responses, question):
    if tipo == '1':
        processor = Processor()
        conteo = {}
        for resp in responses:
            text = resp.text
            nuevo_conteo = processor.process(text)
            conteo = {k: conteo.get(k, 0) + nuevo_conteo.get(k, 0) for k in set(conteo) | set(nuevo_conteo)}
        palabras = {k: v for k, v in conteo.items()}
        return palabras
    else:
        dist = question.distributed_responses(responses)
        return {
            'average': dist['general_avg'],
            'male_avg': dist['males_avg'],
            'female_avg': dist['females_avg'],
            'ages_avg': dist['ages_avg']
        }

def distributed_responses(responses):
    distributed = {}
    rby = [ r.participant for r in responses ]
    ages = [ p.age_in_event for p in rby ]
    distribution = frecuency_dist_ages(ages)
    distributed['males'] = []
    distributed['females'] = []
    distributed['general'] = []
    distributed['ages'] = {}

    for point in distribution:
        distributed['ages'][ point['name'] ] = []
    
    for resp in responses:
        distributed['general'].append(int(resp.result))
        gender = resp.get_gender()
        age = resp.participant.age_in_event
        age = age if age is not None else 0
        if gender =='M':
            distributed['males'].append(int(resp.result))
        elif gender =='F':
            distributed['females'].append(int(resp.result))
        for point in distribution:
            if point['min'] <= age <= point['max']:
                distributed['ages'][point['name'] ].append(int(resp.result))
                break
    distributed['males_avg'] = statistics.mean(distributed['males']) if len(distributed['males'])>0 else 0
    distributed['females_avg'] = statistics.mean(distributed['females']) if len(distributed['females'])>0 else 0
    distributed['general_avg'] = statistics.mean(distributed['general']) if len(distributed['general'])>0 else 0
    distributed['ages_avg']={}
    for point in distribution:
        distributed['ages_avg'][point['name'] ]= statistics.mean(distributed['ages'][point['name'] ]) if len(distributed['ages'][point['name'] ])>0 else 0
    return  distributed
