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
                          lowerLimit=30,
                          upperLimit=170):
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
                val[eachVal] = val[eachVal].strip(".")
        return sectionalDic

    def bulletDropEmailAndWebsite(self, sectionalDic):
        # TODO add the doc string for this function
        for key, val in sectionalDic.items():
            valulist = list()
            for eachVal in range(len(val)):
                if len(FindWebsite(val[eachVal])) < 1 & (FindEmail(val[eachVal]) == False):
                    valulist.append(val[eachVal])
            sectionalDic[key] = valulist
        return sectionalDic

    def removeSpecialChar(self, sectionalDic, specialCharString = "➥|â|€|˜|™|\uf0b7",
                          specialCharList=["â", "€", "˜", "™", "\uf0b7", "➥"]):
        for key, val in sectionalDic.items():
            for eachVal in range(len(val)):
                val[eachVal] = re.sub(specialCharString, "", val[eachVal])
        return sectionalDic

    def isQuestion(self, sectionalDic):

        for key, val in sectionalDic.items():
            valulist = list()
            for eachVal in range(len(val)):
                if val[eachVal][-1] != "?":
                    valulist.append(val[eachVal])
            sectionalDic[key] = valulist
        return sectionalDic

    def hasPhoneNumber(self, sectionalDic):

        phonenumberregex = ["^(\d{3}--\d{3}--\d{4})$",
                            "\+\d{2} \d{9}",
                            " \d{10} ",
                            "\d{2}-\d{9}",
                            "\d{2} \d{4} \d{4}",
                            "\d{4} \d{3} \d{3}",
                            "\d{2} \d{2} \d{2}",
                            "\+\d{2} \d{1} \d{4} \d{4}",
                            "\+\d{2} \d{3} \d{3} \d{3}",
                            "\d{3}-\d{7}",
                            "\d{3} \d{7}",
                            "\d{5}-\d{5}",
                            "\d{5} \d{5}"]

        for key, val in sectionalDic.items():
            valulist = list()
            for eachVal in range(len(val)):
                if True not in [False if re.search(i, val[eachVal]) is None else True for i in phonenumberregex]:
                    valulist.append(val[eachVal])
            sectionalDic[key] = valulist
        return sectionalDic

    def otherCleaning(self, sectionalDic,
                      textList=["apply now", "www", "apply online", "apply today", "click below", "below", "CV"]):

        for key, val in sectionalDic.items():
            valulist = list()
            found = False
            for eachVal in range(len(val)):
                for eachSearchWord in textList:
                    if eachSearchWord.lower() in val[eachVal].lower():
                        found = True
                if found == False:
                    valulist.append(val[eachVal])
            sectionalDic[key] = valulist
        return sectionalDic


def FindWebsite(string):
    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


def FindEmail(string):
    emailaddressregex = "[\w\.-]+@[\w\.-]+"
    if re.search(emailaddressregex, string):
        return True
    else:
        return False
