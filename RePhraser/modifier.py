from lxml import html
import requests
import nltk
import string
from random import randrange
import sqlite3


"""
Dear un-hebrew speakers:
'Tmura' is 'Grammatical modifier': an element that describes the object in sentence.
We love the name 'Tmura', So we use it.

for example:
without Tmura: Lummie and Arad study in Magshimim
with Tmura: Lummie and Arad study in Magshimim, The national cyber project
"""


def cleanText(sen):
    for ch in string.punctuation:
        sentence = sentence.replace(ch, '')
    return sentence


def writeToOurCorpus(sentence):
    """
    Gets a sentence (that contains a tmura) and writes it into the tmura.txt file, so we will have a corpus
    """
    text_file = open("tmura.txt", "a")
    text_file.write(sentence + "\n")
    text_file.close()


def downloadPage(word):
    """
        Gets a word, finds its page in wordnet and downloades it. Returns a correct HTML document,
        which means the parent node is <html>, and there is a body and possibly a head
    """
    search = "http://wordnetweb.princeton.edu/perl/webwn?s="
    search += word
    search += "&sub=Search+WordNet&o2=&o0=1&o8=1&o1=1&o7=&o5=&o9=&o6=&o3=&o4=&h=0" # Builds the url
    page = requests.get(search) # Get page
    return html.fromstring(page.content) # Fromstring creates the correct HTML document


def getTmura(word):
    """
        Gets a word, gets its html page in wordnet (using downloadPage(word)), and returns the tmura of the word.
    """
    tree = downloadPage(word) # Gets the page data
    words = tree.xpath("//div[@class='form']/ul/li/text()") #Gets only the text
    theWord = []
    for i in words:
        if (i != ', '): # We want to take only the first tmura and to clear all of the ', '
            theWord = i
            break
    if (theWord != []): # If found a tmura
        theWord = theWord.split(';')[0].replace(" (", "") # Cleans the tmura from '(' and ')' in the first explenation
        theWord = theWord.split(';')[0].replace(")", "")
        return theWord
    else: # If didn't find a tmura
        return "not found"


def findTmura(word):
    """
        Gets a word, pharses it and finds it tmure. Gets only nouns!!!
        Returns the original word and the tmura- word: tmura
    """
    the_tmura = word + ": " + getTmura(word.replace(" ", "+"))
    #writeToOurCorpus(the_tmura) # Olny if we want to put it in our corpus
    return the_tmura


class Modifier(object):
    """
        It must be a class, so we can call it.
    """
    def change_sentence(self):
        text = nltk.tokenize.word_tokenize(self._sentence)
        changed = False
        for cur in nltk.pos_tag(text):
            if (cur[1] == "NN" or cur[1] == "NNP" or cur[1] == "RPR"):
                foundedTmura = self.getFromDB(cur[0])
                if foundedTmura == None:
                    foundedTmura = getTmura(cur[0])
                    if foundedTmura != "not found":
                        self.add2DB(cur[0], foundedTmura)
                if foundedTmura != "not found" and changed == False:
                    if (foundedTmura.find("OR")):
                        foundedTmura = foundedTmura.replace('OR', 'or')
                    
                    if randrange(2) == 0:
                        rep = cur[0] + ", " + foundedTmura + ", "
                    else:
                        rep = cur[0] + "(" + foundedTmura + ") "
                        
                    self._sentence = self._sentence.replace(cur[0], rep)
                    changed = True
        return self._sentence
        
    def getFromDB(self, word):
        cur = self._conn.cursor()
        cur.execute("SELECT Define FROM tmura WHERE WORD=\""+word.lower()+"\"")
        self._conn.commit()
        rows = cur.fetchall()
        #print "Rows: ",rows
        if len(rows) == 0: # Does'nt exist
            return None
        #print "Rows: ",rows
        return rows[0][0]
    
    def add2DB(self, word, define):
        try:
            self._conn.execute("INSERT INTO tmura (WORD, Define) \
            VALUES (?, ?)", (word.lower(), define.lower()));
            self._conn.commit()
            return True
        except:
            return False
        self._conn.commit()
    
    def addTable(self):
        self._conn.execute('''CREATE TABLE tmura
               (ID INTEGER  PRIMARY KEY  AUTOINCREMENT     NOT NULL,
               WORD TEXT NOT NULL,
               Define TEXT    NOT NULL);''')
        self._conn.commit()
        
    def connectDB(self):
        self._conn = sqlite3.connect('tmura.db')
        
    def disconnectDB(self):
        self._conn.close()

    def __init__(self, sentence):
        """
        :param word: sentence
        :return: sentence with tmura
        """
        self.connectDB()
        #self.addTable()
        self._sentence = sentence
        return None
