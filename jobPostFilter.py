import logging
import re
import operator
import pandas as pd


class jobAddFilter:

    def __init__(self):
        logging.info('paragraphFilters class is called')

    def NumberChar(self, text,
                   lowerLimit=400,
                   upperLimit=5000):
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

        if (len(text) >= lowerLimit) & (len(text) <= upperLimit):
            logging.info('NumberChar(text) returned True')
            return True
        else:
            logging.info('NumberChar(text) returned False')
            return False

    def HasKeywords(self, text):
        sectionaDict = self.detectBullets(text)
        if ("Job Responsibilities" in sectionaDict.keys()) and ("Skills & Experience" in sectionaDict.keys()):
            return True
        else:
            return False

    # def HasKeywords(self, text,
    #                 keywordDic={
    #                     "Job Responsibilities": ["Responsibilities", "Responsible", "Description", "Day-to-day",
    #                                              "Tasks",
    #                                              "Duties", "What you’ll do", "Role", "The opportunity",
    #                                              "The opportunity",
    #                                              "Key Activities", "Functions", "key priorities",
    #                                              "what you'll be doing",
    #                                              "accountabilities", "Key Duties"],
    #                     "Skills & Experience": ["Qualifications",
    #                                             "Skills", "Experience", "looking for", "About You", "Education",
    #                                             "Ideal Candidate",
    #                                             "Possess", "Successful", "Profile", "Requirements",
    #                                             "success in the role", "Attributes",
    #                                             "must have", "Who you are", "you will bring", "to be considered",
    #                                             "Qualified candidates will have",
    #                                             "License", "SELECTION CRITERIA", "following physical capabilities",
    #                                             "Skill", "Physical Demands", "your background",
    #                                             "what we need", "Qualification", "applicants must", "background"]
    #                 }):
    #     """
    #     counts the number of paragraphs in the text and return the count and list of identified paragraphs.
    #     ...
    #
    #     Parameters
    #     ----------
    #     text : str
    #         text data to count paragraphs in the string
    #
    #     Returns
    #     -------
    #     tuple : a tuple containing:
    #         - paracount ([int]): Count of the number of paragraphs
    #         - paragraphs ([list]): List of paragraphs in string format
    #     """
    #
    #     text = text.replace("\n", " ")
    #     text = re.sub("\s\s+", " ", text)
    #     text = text.lower()
    #
    #     hasKeyword = True
    #     for key, val in keywordDic.items():
    #         if (any(word.lower() in text.lower() for word in val)) & (hasKeyword):
    #             hasKeyword = True
    #     if hasKeyword:
    #         logging.info('HasKeywords(text) returned True')
    #         return True
    #     else:
    #         logging.info('HasKeywords(text) returned False')
    #         return False

    # removed role
    # removed Successful
    def detectBullets(self, text, keywordDic={
        "Job Responsibilities": [["Responsibilities", "Responsible", "Description", "Day-to-day",
                                  "Tasks", "Duties", "Functions", "accountabilities", "Responsibilities:"],
                                 ["What you’ll do", "The opportunity",
                                  "Key Activities", "key priorities", "what you'll be doing", "Key Duties",
                                  "Day to day", "About the role", "the role", "day in the life", "We’re looking for",
                                  "Essential Functions:", "Essential Functions",
                                  "Job Summary", "What you’ll be doing:", "be doing", "Successful Candidate",
                                  "What will I be doing"]],
        "Skills & Experience": [["Qualifications", "Skills", "Experience", "Education", "Profile",
                                 "Requirements", "background", "Possess", "License", "Desirable",
                                 "Qualification", "Skill", "Attributes", "Requirements:", "Required"],
                                ["Ideal Candidate", "success in the role", "must have", "Who you are", "you will bring",
                                 "to be considered", "looking for:", "looking for\n", "About You", "looking for",
                                 "Qualified candidates will have", "SELECTION CRITERIA",
                                 "following physical capabilities", "WHAT WE ARE LOOKING FOR", "match if",
                                 "Physical Demands", "your background", "Desirable skills;",
                                 "what we need", "applicants must", "Skills and experience",
                                 "Experience/skills required;",
                                 "Experience/skills required", "Required experience and skills",
                                 "What You Need To Succeed", "To be considered", "Experience / Requirements",
                                 "Desirable skills", "right person", "You must currently have", "must currently have",
                                 "currently have", "Qualification/Skills", "Experience\nRequired", "Job Skills",
                                 "What are we looking for", "Experience / Requirements"]],
        "Benefits": [["Benefits"],
                     ["What you'll get", "We offer", "What's on offer", "Perks", "in it for you",
                      "What we are offering", "We’re offering", "we are offering"]]
    }):

        # TODO add the doc string for this function
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

        sectionalDic = {}
        found = False
        text = re.sub(r"(\w)([A-Z])", r"\1 \2", text)
        for key, val in keywordDic.items():
            for keyword in val[1]:
                if keyword.lower() in text.lower():
                # if len(text.lower().split(keyword.lower())) > 1:
                    # print("(2)Splitting on: " + key + "-" + keyword)
                    sectionalDic[key] = text.lower().split(keyword.lower())[-1]
                    found = True
                    break
            for textchar in text.split():
                if (textchar.lower().strip(":") in [valu.lower() for valu in val[0]]) and (found != True):
                    # print("(1)Splitting on: " + key + "-" + textchar)
                    sectionalDic[key] = text.lower().split(textchar.lower())[-1]
                    break

        countDict = {key: len(value) for key, value in sectionalDic.items()}
        orderedset = sorted(countDict.items(), key=operator.itemgetter(1), reverse=True)
        for key, val in sectionalDic.items():
            sectionalDic[key] = re.split('\n|\.|:|;', val)
        if len(orderedset) > 1:
            for orderSetCount in range(len(orderedset)):
                if orderSetCount + 1 < len(orderedset):
                    sectionalDic[orderedset[orderSetCount][0]] = list(
                        set(sectionalDic[orderedset[orderSetCount + 1][0]]) ^ set(
                            sectionalDic[orderedset[orderSetCount][0]]))

        for key, val in sectionalDic.items():
            sectionalDic[key] = [eachVal.strip("•")
                                     .strip("'*")
                                     .strip("·")
                                     .strip('·')
                                     .strip('!')
                                     .strip().capitalize() for eachVal in val]

        if "Job Responsibilities" in sectionalDic.keys():
            sectionalDic["Job Responsibilities"] = sectionalDic["Job Responsibilities"][:10]
        if "Skills & Experience" in sectionalDic.keys():
            sectionalDic["Skills & Experience"] = sectionalDic["Skills & Experience"][:10]
        if "Benefits" in sectionalDic.keys():
            sectionalDic["Benefits"] = sectionalDic["Benefits"][:5]

        return sectionalDic

    def categoryChecker(self, text, key, fileName="keywords.csv"):

        """
        Based on the CSV fileName "keywords.csv" it assigns the category to each sentence.
        ...

        Parameters
        ----------
        text : str
            text data to to identify the keywords from

        key : str
            the category from which the keywords comes from

        fileName : str
            keywords.csv (Default) CSV file with list of keywords to identify and their category

        Returns
        -------
        str: String character with the category label
        """

        keywordsDataFrame = pd.read_csv(fileName)

        if key == "Job Responsibilities":
            return "A"
        elif key == "Benefits":
            return "I"

        elif key == "Skills & Experience":
            for keyword in keywordsDataFrame.Keywords.values:
                if keyword.lower() in text.lower():
                    charCat = keywordsDataFrame.loc[(keywordsDataFrame.Keywords.str.lower() == keyword.lower()) & ((keywordsDataFrame.loc[:, "Section Heading"] == "Skills & Experience") |
                                                                     (keywordsDataFrame.loc[:, "Section Heading"] == "Education Level") |
                                                                     (keywordsDataFrame.loc[:, "Section Heading"] == "Amount of Experience") |
                                                                     (keywordsDataFrame.loc[:, "Section Heading"] == "Licenses/Tickets") |
                                                                     (keywordsDataFrame.loc[:, "Section Heading"] == "Programs") |
                                                                     (keywordsDataFrame.loc[:, "Section Heading"] == "Checks/Trainings") |
                                                                     (keywordsDataFrame.loc[:, "Section Heading"] == "Working Rights")), "Categorisation"]
                    if len(charCat) > 0:
                        return (charCat.values[0])

                    else:
                        return 'B'
        else:
            return 'B'

        return ("B")

    def removeIntroduction(self, text, keywords=["Responsibilities", "Responsible", "Description", "Day-to-day",
                                                 "Tasks", "Duties", "Functions", "accountabilities",
                                                 "Responsibilities:",
                                                 "What you’ll do", "The opportunity",
                                                 "Key Activities", "key priorities", "what you'll be doing",
                                                 "Key Duties",
                                                 "Day to day", "About the role", "the role", "day in the life",
                                                 "We’re looking for",
                                                 "Essential Functions:", "Essential Functions",
                                                 "Job Summary", "What you’ll be doing:", "be doing",
                                                 "Successful Candidate", "What will I be doing",
                                                 "Qualifications", "Skills", "Experience", "Education", "Profile",
                                                 "Requirements", "background", "Possess", "License", "Desirable",
                                                 "Qualification", "Skill", "Attributes", "Requirements:", "Required",
                                                 "Ideal Candidate", "success in the role", "must have", "Who you are",
                                                 "you will bring",
                                                 "to be considered", "looking for:", "looking for\n", "About You",
                                                 "looking for",
                                                 "Qualified candidates will have", "SELECTION CRITERIA",
                                                 "following physical capabilities", "WHAT WE ARE LOOKING FOR",
                                                 "match if",
                                                 "Physical Demands", "your background", "Desirable skills;",
                                                 "what we need", "applicants must", "Skills and experience",
                                                 "Experience/skills required;",
                                                 "Experience/skills required", "Required experience and skills",
                                                 "What You Need To Succeed", "To be considered",
                                                 "Experience / Requirements",
                                                 "Desirable skills", "right person", "You must currently have",
                                                 "must currently have",
                                                 "currently have", "Qualification/Skills", "Experience\nRequired",
                                                 "Job Skills", "What are we looking for", "Experience / Requirements"]):

        for keyword in keywords:
            splittext = text.lower().split(keyword.lower())
        if len(splittext) > 1:
            return splittext[-1]



