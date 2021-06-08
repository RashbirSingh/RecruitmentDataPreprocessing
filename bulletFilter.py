import logging
import spacy
import en_core_web_trf

class bulletFilter:

    def __init__(self):
        self.nlp = en_core_web_trf.load()
        logging.info('bulletFilter class is called')

    def recordCharCounter(self,
                          sectionalDic,
                          lowerLimit = 30,
                          upperLimit = 170):
        for key, val in sectionalDic.items():
            valulist = list()
            for eachVal in range(len(val)):
                if (len(val[eachVal]) > lowerLimit) & (len(val[eachVal]) <= upperLimit):
                    valulist.append(val[eachVal])
                sectionalDic[key] = valulist
        return sectionalDic

    def bulletEntityRecognister(self, sectionalDic, entityName: str = 'ORG'):
        for key, val in sectionalDic.items():
            valulist = list()
            for eachVal in range(len(val)):
                doc = self.nlp(val[eachVal])
                if entityName not in [entity.label_ for entity in doc.ents]:
                    valulist.append(val[eachVal])
                sectionalDic[key] = valulist
        return sectionalDic


    def removeDot(self, sectionalDic):
        for key, val in sectionalDic.items():
            for eachVal in range(len(val)):
                val[eachVal] == val[eachVal].strip(".")
        return sectionalDic