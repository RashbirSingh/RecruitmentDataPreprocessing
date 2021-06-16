import logging
import spacy
import en_core_web_trf
import re

class bulletFilter:

    def __init__(self):
        self.nlp = en_core_web_trf.load()
        logging.info('bulletFilter class is called')

    def recordCharCounter(self,
                          sectionalDic,
                          lowerLimit = 30,
                          upperLimit = 170):
        # TODO add the doc string for this function
        for key, val in sectionalDic.items():
            valulist = list()
            for eachVal in range(len(val)):
                if (len(val[eachVal]) >= lowerLimit) & (len(val[eachVal]) <= upperLimit):
                    valulist.append(val[eachVal])
                sectionalDic[key] = valulist
        return sectionalDic

    def bulletEntityRecognister(self, sectionalDic, entityName: str = 'ORG'):
        # TODO add the doc string for this function
        for key, val in sectionalDic.items():
            valulist = list()
            for eachVal in range(len(val)):
                doc = self.nlp(val[eachVal])
                if entityName not in [entity.label_ for entity in doc.ents]:
                    valulist.append(val[eachVal])
                sectionalDic[key] = valulist
        return sectionalDic


    def removeDot(self, sectionalDic):
        # TODO add the doc string for this function
        for key, val in sectionalDic.items():
            for eachVal in range(len(val)):
                val[eachVal] == val[eachVal].strip(".")
        return sectionalDic

    def bulletDropEmailAndWebsite(self, sectionalDic):
        # TODO add the doc string for this function
        for key, val in sectionalDic.items():
            valulist = list()
            for eachVal in range(len(val)):
                if (re.match("((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", val[eachVal]) == False) & \
                        (re.match("@" , val[eachVal]) == False):
                    valulist.append(val[eachVal])
                sectionalDic[key] = valulist
        return sectionalDic