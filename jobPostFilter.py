import logging
import re
import operator


class jobAddFilter:

    def __init__(self):
        logging.info('paragraphFilters class is called')

    def NumberChar(self, text,
                   lowerLimit=400,
                   upperLimit=2000):
        """
        counts the number of paragraphs in the text and return the count and list of identified paragraphs.
        ...

        Parameters
        ----------
        text : str
            text data to count paragraphs in the string

        Returns
        -------
        tuple : a tuple containing:
            - paracount ([int]): Count of the number of paragraphs
            - paragraphs ([list]): List of paragraphs in string format
        """

        if (len(text) > lowerLimit) & (len(text) < upperLimit):
            logging.info('NumberChar(text) returned True')
            return True
        else:
            logging.info('NumberChar(text) returned False')
            return False

    def HasKeywords(self, text,
                    keywordDic={
                        "Job Responsibilities": ["Responsibilities", "Responsible", "Description", "Day-to-day",
                                                 "Tasks",
                                                 "Duties", "What you’ll do", "Role", "The opportunity",
                                                 "The opportunity",
                                                 "Key Activities"],
                        "Skills & Experience": ["Skills", "Experience", "looking for", "About You", "Education",
                                                "Ideal Candidate",
                                                "Possess", "Successful", "Profile", "Requirements",
                                                "success in the role", "Attributes",
                                                "must have", "Who you are", "you will bring", "to be considered",
                                                "Qualifications",
                                                "License", "SELECTION CRITERIA"]
                    }):
        """
        counts the number of paragraphs in the text and return the count and list of identified paragraphs.
        ...

        Parameters
        ----------
        text : str
            text data to count paragraphs in the string

        Returns
        -------
        tuple : a tuple containing:
            - paracount ([int]): Count of the number of paragraphs
            - paragraphs ([list]): List of paragraphs in string format
        """

        text = text.replace("\n", " ")
        text = re.sub("\s\s+", " ", text)
        text = text.lower()
        # if len(set(keywordsToDetect) & set(text.lower().split())) > 0:
        # for keyword in keywordsToDetect:
        #     if len(text.lower().split(keyword.lower())) > 1:
        #         logging.info('HasKeywords(text) returned True')
        #         return True
        #     else:
        #         logging.info('HasKeywords(text) returned False')
        #         return False
        hasKeyword = True
        for key, val in keywordDic:
            if (any(word in text for word in val)) & (hasKeyword):
                hasKeyword = True
        if hasKeyword:
            logging.info('HasKeywords(text) returned True')
            return True
        else:
            logging.info('HasKeywords(text) returned False')
            return False

    def detectBullets(self, text, keywordDic={
        "Job Responsibilities": ["Responsibilities", "Responsible", "Description", "Day-to-day", "Tasks",
                                 "Duties", "What you’ll do", "Role", "The opportunity", "The opportunity",
                                 "Key Activities"],
        "Skills & Experience": ["Skills", "Experience", "looking for", "About You", "Education", "Ideal Candidate",
                                "Possess", "Successful", "Profile", "Requirements", "success in the role", "Attributes",
                                "must have", "Who you are", "you will bring", "to be considered", "Qualifications",
                                "License", "SELECTION CRITERIA"],
        "Benefits": ["Benefits", "What you'll get", "We offer", "What's on offer", "Perks", "in it for you",
                     "What we are offering"]
    }):
        sectionalDic = {}
        for key, val in keywordDic.items():
            for keyword in val:
                if len(text.lower().split(keyword.lower())) > 1:
                    sectionalDic[key] = text.lower().split(keyword.lower())[-1]
                    break

        countDict = {key: len(value) for key, value in sectionalDic.items()}
        orderedset = sorted(countDict.items(), key=operator.itemgetter(1), reverse=True)
        # TODO: Manage this try catch
        for key, val in sectionalDic.items():
            sectionalDic[key] = val.split('\n')

        if len(orderedset) > 1:
            for orderSetCount in range(len(orderedset)):
                if orderSetCount + 1 < len(orderedset):
                    sectionalDic[orderedset[orderSetCount][0]] = list(
                        set(sectionalDic[orderedset[orderSetCount + 1][0]]) ^ set(
                            sectionalDic[orderedset[orderSetCount][0]]))
                    # sectionalDic[orderedset[orderSetCount][0]] = re.sub(sectionalDic[orderedset[orderSetCount + 1][0]],
                    #                                                     "",
                    #                                                     sectionalDic[orderedset[orderSetCount][0]])

        return sectionalDic

    # def detectStartEnd(self, text, keywordDic={
    #     "Job Responsibilities": ["Responsibilities", "Responsible", "Description", "Day-to-day", "Tasks",
    #                              "Duties", "What you’ll do", "Role", "The opportunity", "The opportunity"],
    #     "Skills & Experience": ["Skills", "Experience", "looking for", "About You", "Education", "Ideal Candidate",
    #                             "Possess", "Successful", "Profile", "Requirements", "success in the role", "Attributes",
    #                             "must have", "Who you are", "you will bring", "to be considered", "Qualifications",
    #                             "License"],
    #     "Benefits": ["Benefits", "What you'll get", "We offer", "What's on offer", "Perks", "in it for you",
    #                  "What we are offering"]
    # }):
