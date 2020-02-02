import re

import os
import json

from nltk.tokenize import TweetTokenizer

import numpy as np

neutralWords = set(['poner', 'senor', 'venderme', 'serie', 'pasa', 'paso', 'decir', 'ahora',
                    'mail', 'mails', 'texto', 'textos', 'dos', 'tres', 'cuatro', 'cinco',
                    'seis', 'siete', 'ocho', 'nueve', 'diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciseis',
                    'diecesiete',
                    'dieciocho', 'diecinueve', 'veinte', 'mes', 'dia', 'dias', 'meses', 'ano', 'anos', 'cliente',
                    'me', 'esa', 'el', 'la', 'los', 'de', 'por', 're', 'a', 'mi', 'ma', 'de', 'por', 'el', 'ser',
                    'estar',
                    'como', 'en', 'con', 'una', 'un', 'uno', 'y', 'que', 'su', 'sus', 'les', 'al', 'se', 'te', 'le',
                    'lo', 'ud', 'uds', 'ustedes',
                    'ese', 'este', 'eso', 'esto', 'esta', 'estas', 'estos', 'estes', 'esos', 'esas', "/", "-",
                    'eses', 'para', 'por', 'unas', 'unos', 'o', 'porque', 'entre', 'cuando', 'sobre', 'tambien',
                    'durante', 'otro',
                    'otros', 'ante', 'antes', 'algunos', 'algunas', 'algun', 'cual', 'os', 'mios', 'mias', 'mio', 'mio',
                    'rt', 'asi'
                          'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuetro', 'nuetras',
                    'nuestros', 'nuestras', "/",
                    'vuestro', 'vuestra', 'vuestros', 'vuestras', 'he', 'has', 'ha', 'han', 'hemos', 'habeis', 'haya',
                    'aqui', 'aqua', 'ahi', 'asi', '¿', 't', 'htps', 'muy', '-'
                                                                           'alli', 'alla', 'k', 'q', 'qu', 'son',
                    'desde', 'es', 'ya', 'usted', 'de', 'nos', 'del', 'son', 'sos', 'vos', 'e', 'am', 'pm', 'las',
                    'http'])

negWords = ['no', 'tampoco', 'ni', 'nunca', 'sin', 'nadie', 'jamas', 'nada', 'ningun', 'ninguno', 'poco']
stopNeg = [',', '!', '.', '(', ')', '[', ']', ':', ';', 'pero', '?', 'con', 'porque', 'y', 'ninguno', 'ningun',
           'no', 'tampoco', 'ni', 'nunca', 'sin', 'nadie', 'jamas', 'nada']
ponctuation = list("[.,:;!?@]()¡…")
# constantes
path = './'
dirtyReps = re.compile(r'([^lL0])\1{1,}')
dirtySpaces = re.compile(r'(\.|,|:|;|!|\?|\[|\]|\(|\))[A-Za-z0-9]+')
dirtyK = re.compile('[^o]k')
dirtyJaja = re.compile(r'[ja]{5,}')
dirtyJeje = re.compile(r'[je]{5,}')
numbers = re.compile(r'[0-9]+')

uglySeparator = '---A-REAL-UGLY-SEPARATOR---'

with open(os.path.dirname(os.path.abspath(__file__)) + '/DictConjug.json', 'r') as f:
    dictConjug = json.load(f)


class Processor:
    def __init__(self, neutralWords=neutralWords, verbose=False):
        self.verbose = verbose
        self.neutralWords = neutralWords
        return

    def binarize(self, r):
        if r >= 4:
            return 1
        elif r <= 2.5:
            return 0
        else:
            return np.nan

    def replaceAccents(self, word):
        word = word.replace('í', 'i')
        word = word.replace('ó', 'o')
        word = word.replace('ò', 'o')
        word = word.replace('ñ', 'n')
        word = word.replace('é', 'e')
        word = word.replace('è', 'e')
        word = word.replace('á', 'a')
        word = word.replace('à', 'a')
        word = word.replace('ü', 'u')
        word = word.replace('ú', 'u')
        word = word.replace('ö', 'o')
        word = word.replace('ë', 'e')
        word = word.replace('ï', 'i')
        return word

    def processDetails(self, word):
        word = word.replace(' re comen', ' recomen')
        word = word.replace(' re ', ' muy ')
        word = word.replace(' 100% ', ' muy ')
        word = word.replace('mercado libre', uglySeparator.join(['mercado', 'libre']))
        word = word.replace(' x ', ' por ')
        word = word.replace(' q ', ' que ')
        word = word.replace(' k ', ' que ')
        return word

    def processJaja(self, word):
        while dirtyJaja.search(word) != None:
            word = word.replace(dirtyJaja.search(word).group(), 'jaja')
        while dirtyJeje.search(word) != None:
            word = word.replace(dirtyJeje.search(word).group(), 'jaja')
        return word

    def processRep(self, word):
        '''la doble L atencion !!!!'''
        while dirtyReps.search(word) != None:
            word = word.replace(dirtyReps.search(word).group(), dirtyReps.search(word).group()[0])
        return word

    def processSpaces(self, word):
        while dirtySpaces.search(word) != None:
            word = word.replace(dirtySpaces.search(word).group()[0], dirtySpaces.search(word).group()[0] + ' ')
        return word

    def processK(self, word):
        while dirtyK.search(word) != None:
            word = word.replace(dirtyK.search(word).group(), dirtyK.search(word).group()[0] + 'qu')
        return word

    def processNumbers(self, word):
        # word = word.replace('1000',uglySeparator+'mil')
        # word = word.replace('100',uglySeparator+'cien')
        # word = word.replace('10',uglySeparator+'diez')
        while numbers.search(word) != None:
            word = word.replace(numbers.search(word).group(), '')
        # word = word.replace(uglySeparator+'mil','1000')
        # word = word.replace(uglySeparator+'cien','100')
        # word = word.replace(uglySeparator+'diez','10')
        return word

    def processPoint(self, x):
        if len(x) == 0:
            return x
        else:
            if x[-1] in stopNeg:
                return x
            else:
                return x + '.'

    def processNeg(self, tokens):
        negIndexes = [i for i, j in enumerate(tokens) if j in negWords]
        for negWord in negIndexes:
            j = np.infty
            for f in stopNeg:
                try:
                    j_ = max(tokens[(negWord + 1):].index(f), 0)
                    j = min(j, j_)
                except:
                    continue
            if j < np.infty:
                j = j + 1
                for k in range(negWord + 1, (min(3, int(j)) + negWord)):
                    if tokens[k] not in stopNeg:
                        tokens[k] = 'not_' + tokens[k]
        # return [w for w in tokens if w not in negWords]
        return tokens

    def replaceVerbs(self, x):
        if len(x) == 0:
            x = x
        else:
            addBack = False
            if x[-1] in ponctuation:
                endPonctu = x[-1]
                addBack = True
                x = x[:-1]
            for infinitif in dictConjug.keys():
                foundMatch = any(e in x.replace(' ', '_') for e in set(dictConjug[infinitif]))
                if foundMatch == False:
                    pass
                else:
                    x = x.replace(' ', '_')
                    matches = [e for e in set(dictConjug[infinitif]) if '_' + e + '_' in x]
                    for e in matches:
                        x = x.replace('_' + e + '_', '_' + infinitif + '_')
                    del matches
                    if x.split('_')[0] in set(dictConjug[infinitif]):
                        x = x.replace(x.split('_')[0] + '_' + x.split('_')[1] + '_' + x.split('_')[2],
                                      infinitif + '_' + x.split('_')[1] + '_' + x.split('_')[2])
                    if '_'.join(x.split('_')[:2]) in set(dictConjug[infinitif]):
                        x = x.replace('_'.join(x.split('_')[:2]) + '_' + x.split('_')[2] + '_' + x.split('_')[3],
                                      infinitif + '_' + x.split('_')[2] + '_' + x.split('_')[3])
                    if x.split('_')[-1] in set(dictConjug[infinitif]):
                        x = x.replace(x.split('_')[-3] + '_' + x.split('_')[-2] + '_' + x.split('_')[-1],
                                      x.split('_')[-3] + '_' + x.split('_')[-2] + '_' + infinitif)
                    if '_'.join(x.split('_')[-2:]) in set(dictConjug[infinitif]):
                        x = x.replace(x.split('_')[-4] + '_' + x.split('_')[-3] + '_' + '_'.join(x.split('_')[-2:]),
                                      x.split('_')[-4] + '_' + x.split('_')[-3] + '_' + infinitif)

                    x = x.replace('_', ' ')
            if addBack:
                x = x + endPonctu
            return x

    def process(self, x):
        try:
            str(x).replace('\r', '').replace('\n', '')
            x = self.replaceAccents(x.lower())
            x = self.processDetails(x)
            x = self.processRep(x)
            x = self.processJaja(x)
            x = self.processSpaces(x)
            x = self.processPoint(x)
            x = self.processK(x)

            twwettokenizer = TweetTokenizer()

            tokens = twwettokenizer.tokenize(self.replaceVerbs(x))
            tokens = [t for t in tokens if t not in neutralWords]
            tokens = [t for t in tokens if t not in ponctuation]
            # tokens = [t for t in tokens if t not in uselessWords]
        except Exception as e:
            print(e)
            raise

        textolimpio = ' '.join(str(re.sub('[?;,;:!"\(\)\'.]', '', ' '.join(tokens))).split()).replace(uglySeparator,
                                                                                                      '_')
        nuevoaaray = textolimpio.replace(' ', '*').split('*')

        conteo = {k: nuevoaaray.count(k) for k in nuevoaaray}

        return conteo

