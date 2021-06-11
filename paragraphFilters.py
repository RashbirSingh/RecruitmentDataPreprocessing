import re
import nltk
import logging
import spacy
import en_core_web_trf


# python -m spacy download en_core_web_trf
# nltk.download('punkt')

class paragraphFilters:

    def __init__(self):
        self.nlp = en_core_web_trf.load()
        logging.info('paragraphFilters class is called')

    # TODO: Ask about how to identify start and end paragraph
    def countParagraph(self, text):
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

        logging.info('Counting number of paragraphs')
        paracount = 0
        paragraphs = []
        text = re.sub("\n \n", "\n\n", text)
        for i in re.finditer(r'(?s)((?:[^\n][\n]?)+)', text):
            paracount = paracount + 1
            paragraphs.append(text[i.start(): i.end() + 1])
        return (paracount, paragraphs)

    def ParagraphCharCountFilter(self, ListOfTextParagraph: list):
        """
        Filter to count characters in each paragraph
        ...

        Parameters
        ----------
        ListOfTextParagraph : list
            list of paragraphs in text format (List of string paragraphs)


        Returns
        -------
        list
            list of paragraphs that has character count between 400 and 2000
        """

        logging.info('Counting number of characters in a paragraph')
        for para in ListOfTextParagraph:
            if (len(para) >= 400 & len(para) <= 2000) == False:
                ListOfTextParagraph.remove(para)
        return ListOfTextParagraph

    def ParagraphSentCountFilter(self, ListOfTextParagraph: list):
        """
        Filter to count sentences in each paragraph
        ...

        Parameters
        ----------
        ListOfTextParagraph : list
            list of paragraphs in text format (List of string paragraphs)


        Returns
        -------
        list
            list of paragraphs that has sentences between 2 and 4
        """

        logging.info('Counting number of sentences in a paragraph')
        for para in ListOfTextParagraph:
            if (len(nltk.sent_tokenize(para)) > 2 & len(nltk.sent_tokenize(para)) <= 4) == False:
                ListOfTextParagraph.remove(para)
        return ListOfTextParagraph

    def ParagraphEntityRecognister(self, ListOfTextParagraph: list, entityName: str = 'ORG'):
        """
        Filter to find if entity type name is listed in the paragraph
        ...

        Parameters
        ----------
        ListOfTextParagraph : list
            list of paragraphs in text format (List of string paragraphs)


        Returns
        -------
        list
            list of paragraphs that has entity type in the paragraph

        REFER
        -----
        https://towardsdatascience.com/named-entity-recognition-with-nltk-and-spacy-8c4a7d88e7da
        """

        for para in ListOfTextParagraph:
            doc = self.nlp(para)
            if entityName not in [entity.label_ for entity in doc.ents]:
                ListOfTextParagraph.remove(para)
        return ListOfTextParagraph

    def phoneNumberDetection(self, ListOfTextParagraph):
        """
        Filter to find if paragraph have phoneNumber or not
        ...

        Parameters
        ----------
        ListOfTextParagraph : list
            list of paragraphs in text format (List of string paragraphs)


        Returns
        -------
        list
            list of paragraphs that do not has phone number in the paragraph
        """

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

        for para in ListOfTextParagraph:
            if True in [False if re.search(i, para) is None else True for i in phonenumberregex]:
                ListOfTextParagraph.remove(para)
        return ListOfTextParagraph

    def emailDetection(self, ListOfTextParagraph):
        """
        Filter to paragraph have email or not
        ...

        Parameters
        ----------
        ListOfTextParagraph : list
            list of paragraphs in text format (List of string paragraphs)


        Returns
        -------
        list
            list of paragraphs that do not has email in the paragraph
        """

        emailaddressregex = "[\w\.-]+@[\w\.-]+"
        for para in ListOfTextParagraph:
            if re.search(emailaddressregex, para):
                ListOfTextParagraph.remove(para)
        return ListOfTextParagraph


