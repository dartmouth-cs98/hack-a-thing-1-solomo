# Author: Moyosore Okeremi

import requests
import json
import twitter
import operator
from datetime import date
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout, QMessageBox)
import sys


# Azure Portal > Text Analytics API Resource > Keys
ACCESS_KEY = 'c02852480cd448049e7a351b8d4d58cd'
# Text Analytics API Base URL
URL = 'https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/'

#Variables that contains the user credentials to access Twitter API
access_token = '337866142-3qT8u1lW5gSufVwHrsbkn9ndnsLzSvoy09P67e64'
access_token_secret = 'mxvQaHgZ6fRhwRbXDi5ocrjuKSIL3gGsauo5XWamGc3MS'
api_key = 'JVEXa288QikhVQtOWzsl48TJ3'
api_key_secret = 'qnnTXV9K0H9PQYXG4wviJdbLTaN4Bi8FrCQgszJq7zIu3DtUO2'

monthNum = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

def plot(xvalues, yvalues, annotations, xbarvals, ybarvals):
    fig = plt.figure()

    ax = fig.add_subplot(211)
    ax.set_title('Average Sentiment Score Per Day')
    lines = ax.plot(yvalues,xvalues, 'go', yvalues,xvalues, 'g')
    annot = ax.annotate("", xy=(0, 0), xytext=(0.05,0.05), verticalalignment='top', textcoords="offset points",wrap=True,
                        bbox=dict(boxstyle="round", fc="w"))
    annot.set_visible(False)

    def update_annot(ind):

        x, y = lines[0].get_data()
        annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = "{}".format(" ".join([annotations[n] for n in ind["ind"]]))
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(1)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = lines[0].contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                annot.set_zorder(10)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    ax.set_xlabel('Days Ago')
    ax.set_ylabel('Sentiment Score')
    ax.set_xlim(left=0)

    ax2 = fig.add_subplot(212)
    ax2.bar(np.arange(len(xbarvals)), ybarvals, align='center', alpha=0.5)
    ax2.set_xticks(np.arange(len(xbarvals)))
    ax2.set_xticklabels(xbarvals, rotation='vertical')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Popular Key Phrases')

    plt.tight_layout()
    plt.show()

def get_score_statement(score, username):
    if score <=0.2:
        return "@"+ username + " was deep deep in the dumps today :("
    if score <= 0.4:
        return "@"+ username + " could probably use a big bear hug today"
    if score <=0.6:
        return "Nothing wrong with having just a basic day."+"@"+ username +" has no strong emotions today"
    if score <= 0.8:
        return " Things are on the up and up for " +"@"+ username +" :)"
    if score <=1:
        return "Yes! Lots of positivity in the life of "+"@"+ username + " today! Keep it up!"

def get_insights(api, documents):
    """
    Get insights using Microsoft Cognitive Service - Text Analytics
    """
    # 1. Set a Request Header to include the Access Key
    headers = {'Ocp-Apim-Subscription-Key': ACCESS_KEY}
    # 2. Set the HTTP endpoint
    url = URL + api
    # 3. Create a POST request with the JSON documents
    request = requests.post(url, headers=headers, data=json.dumps(documents))
    # 4. Load Response
    response = json.loads(request.content)
    return response['documents']


def find_days_between(first, last):
    return abs((last - first).days)

def find_date_form(createdAt):
    split = createdAt.split(' ')
    return date(int(split[len(split) -1]), monthNum[split[1]], int(split[2]))

def find_period(tweets):
    first = datetime.now().strftime("%Y-%m-%d")
    last = tweets[len(tweets) - 1]['created_at']
    return find_days_between(datetime.strptime(first, '%Y-%m-%d').date(), find_date_form(last))

class Dialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(Dialog, self).__init__()
        self.userName = QLineEdit()
        self.tweets = QLineEdit()
        self.keyPhrase = QLineEdit()
        self.createFormGroupBox()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Form Layout - pythonspot.com")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Form layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Twitter UserName:"), self.userName)
        layout.addRow(QLabel("Number of Tweets:"), self.tweets)
        layout.addRow(QLabel("Top N KeyPhrases:"), self.keyPhrase)
        self.formGroupBox.setLayout(layout)

    def pop_up_error(self, text):
        QMessageBox.question(self, 'Message - pythonspot.com', text, QMessageBox.Ok,
                             QMessageBox.Ok)
    def accept(self):
        if self.userName.text() != "" and self.tweets.text()!="" and self.keyPhrase.text() != "" :
            try:
                tweetCount = int(self.tweets.text())
                nPopWords = int(self.keyPhrase.text())
            except ValueError:
                self.pop_up_error("Number of tweets and keyPhrases must be INTEGERS")
                return

            if tweetCount >= 1:
                wordFrequency = {}
                api = twitter.Api(consumer_key=api_key,
                                  consumer_secret=api_key_secret,
                                  access_token_key=access_token,
                                  access_token_secret=access_token_secret)
                try:
                    t = api.GetUserTimeline(screen_name=self.userName.text(), count=tweetCount)
                except:
                    self.pop_up_error("username entered does not exist")
                    return

                tweets = [i.AsDict() for i in t]
                if len(tweets)<1:
                    self.pop_up_error("This user has no tweets!")
                    return

                documents = {
                    'documents': tweets
                }

                # handle keyPhrases
                keyP_docs = get_insights('keyPhrases', documents)
                for doc in keyP_docs:
                    for word in doc['keyPhrases']:
                        if word != "RT":
                            if (word in wordFrequency.keys()):
                                wordFrequency[word] += 1
                            else:
                                wordFrequency[word] = 1
                freq_descending = sorted(wordFrequency.items(), key=operator.itemgetter(1), reverse=True)

                # handle sentiment Analysis
                sent_docs = get_insights('sentiment', documents)

                # calculate average sentiment per day available # x = day, y = sentiment
                xvalues = []
                yvalues = []
                annotations = []
                currDate = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), '%Y-%m-%d').date()
                i = 0
                while i < len(tweets):
                    start = find_date_form(tweets[i]['created_at'])
                    count = 1
                    sum = sent_docs[i]['score']
                    i += 1
                    while i < len(tweets) and find_date_form(tweets[i]['created_at']) == start:
                        count += 1
                        sum += sent_docs[i]['score']
                        i += 1
                    xvalues.append(sum / count)
                    yvalues.append(find_days_between(start, currDate))
                    annotationStr = str(start) +'\n' +"score: "+str(sum/count)+"\n" + get_score_statement(sum/count, self.userName.text())
                    annotations.append(annotationStr)
                xbarvals = []
                ybarvals = []
                for pairInd in range(0, nPopWords):
                    if pairInd == len(freq_descending):
                        break
                    xbarvals.append(freq_descending[pairInd][0])
                    ybarvals.append(freq_descending[pairInd][1])
                plot(xvalues, yvalues, annotations, xbarvals, ybarvals)
            else:
                self.pop_up_error("Tweet Count must be greater than 0")
        else:
            self.pop_up_error("No field must be left empty!")

def main():
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())

main()
