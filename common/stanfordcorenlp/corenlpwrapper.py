import json

from .corenlpfactory import CoreNLPFactory

class CoreNLPWrapper:

    __corenlp = None

    def __init__(self):
        self.__corenlp = CoreNLPFactory.createCoreNLP()

    def annotate(self, contents, properties):
        if not 'outputFormat' in properties.keys():
            properties.update({'outputFormat': 'json'})

        try:
            text = self.__corenlp.annotate(contents, properties)
            decodedcontents = json.loads(text)
        except Exception:
            print('\nJSON decoding failed - check CoreNLP return:\n\n' + text + '\n')
            raise
            
        return decodedcontents
