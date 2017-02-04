#!/usr/bin/python
'''
Author: Suruchi Shah
<Explain the purpose and functionality of script>
Usage: python extractEmailContent.py [emailFile] [sourcefile]
'''
import sys
import os
import pprint
import json
import jsonrpclib
from simplejson import loads
from dateutil.parser import parse
#import feature extractor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
#import svm
from sklearn.linear_model import SGDClassifier
#I think scipy need this
import numpy as np
import pickle

class EmailContent(object):
	def __init__(self):
		self.Init()

	def Init(self):
		self.emailFile = sys.argv[1]
		self.sourceFile = sys.argv[2]
		self.emailDictionary = []
		self.sourceDomainDictionary = {}
		self.populateSourceDomainDictionary()

	def getRawText(self):
		with open(self.emailFile, "r") as f:
			content = "\n".join(line.rstrip() for line in f)

		# Split on </email> to separate out the emails
		emailRawTexts = []
		emailRawTexts = content.split("</EMAIL>")

		# For each email, extract the individual pieces of data
		for emailRaw in emailRawTexts:
			if len(emailRaw.strip()) > 1:
				self.extractEmailInformation(emailRaw)

		self.generateFinalOutputJSON()
	
	def extractEmailInformation(self, emailRaw):
		# Remove <email> tag
		emailRaw = emailRaw.replace("<EMAIL>", "")
		contentLines = emailRaw.split("\n")
		emailContent = {}
		for line in contentLines:
			if len(line.strip()) < 2:
				continue
			
			if line.startswith("EMAILID:"):
				emailContent["EMAILID"] = line.replace("EMAILID:", "")

			elif line.startswith("FROM:"):
				emailContent["SENDER"] = line.replace("FROM:", "")
				emailContent["SENDERSOURCE"] = self.getEmailSource(line)
			
			elif line.startswith("RECIPIENT:"):
				emailContent["RECIPIENT"] = line.replace("RECIPIENT:", "")
			
			elif line.startswith("RECEIVEDATE:"):
				emailContent["RECEIVEDATE"] = line.replace("RECEIVEDATE:", "")
			
			elif line.startswith("SENTDATE:"):
				emailContent["SENTDATE"] = line.replace("SENTDATE:", "")
		
			elif line.startswith("SUBJECT:"):
				emailContent["SUBJECT"] = line.replace("SUBJECT:", "")

			elif line.startswith("CONTENT:"):
				emailContent["RAWCONTENT"] = line.replace("RAWCONTENT:", "")
				emailContent["TYPE"] = self.getType(emailContent)

			else:
				emailContent["RAWCONTENT"] = emailContent["RAWCONTENT"] + "\n" + line

		emailContent["CONTENT"] = self.getRelevantContent(emailContent)
		self.emailDictionary.append(emailContent)

	# This method opens the file containing source domain and populates the dictionary with the information
	def populateSourceDomainDictionary(self):
		with open(self.sourceFile, "r") as f:
			content = f.readlines()

		for line in content:
			line = line.strip()
			key, value = line.split("=")
			self.sourceDomainDictionary[value] = key

	# This method extracts the domain source of the email and returns the key
	def getEmailSource(self, senderText):
		domain = senderText[senderText.index("@")+1:senderText.index("com")-1]
		for key, value in self.sourceDomainDictionary.iteritems():
			if key in domain:
				return value

	# This method defines the flow of logic to get the type of email depending on source
	def getType(self, emailContent):
		if emailContent["SENDERSOURCE"] == "PIAZZA":
			return self.getPiazzaType(emailContent["RAWCONTENT"])
		else:

#c = pickle.load( open( "count_vect", "rb" ) )
#t = pickle.load( open( "tfidf_transformer", "rb" ) )
#Amd_clf = pickle.load( open( "Amd.clf", "rb" ) )
#X_test_counts = c.transform(["test test I just want to check whether the e-mail classification is working."])
#X_test_tfidf = t.transform(X_test_counts)
#Amd_predicted = Amd_clf.predict(X_test_tfidf)
			text = emailContent["RAWCONTENT"][8:]
			path = "./export/"
                        ofile = open("test.out","w")
                        print text
			count_vect = pickle.load( open( path+ "count_vect", "rb" ) )
                        tfidf_transformer = pickle.load( open( path+ "tfidf_transformer", "rb" ) )
                        Amd_clf = pickle.load( open( path+ "Amd.clf", "rb" ) )
                        Cmt_clf = pickle.load( open( path+ "Cmt.clf", "rb" ) )
                        Dlv_clf = pickle.load( open( path+ "Dlv.clf", "rb" ) )
#                        DlvCmt_clf = pickle.load( open( path+ "DlvCmt.clf", "rb" ) )
                        Prop_clf = pickle.load( open( path+ "Prop.clf", "rb" ) )
                        Req_clf = pickle.load( open( path+ "Req.clf", "rb" ) )
#                        ReqAmdProp_clf = pickle.load( open( path+ "ReqAmdProp.clf", "rb" ) )
#                        ReqProp_clf = pickle.load( open( path+ "ReqProp.clf", "rb" ) )
			X_test_counts = count_vect.transform([text])
#                        print X_test_counts.shape
			X_test_tfidf = tfidf_transformer.transform(X_test_counts)
#			Amd_predicted = Amd_clf.predict(X_test_tfidf)
#                        print Amd_predicted.shape
#                        Cmt_predicted = Cmt_clf.predict(X_test_tfidf)
#                        Dlv_predicted = Dlv_clf.predict(X_test_tfidf)
#                        DlvCmt_predicted = DlvCmt_clf.predict(X_test_tfidf)
                        Prop_predicted = Prop_clf.predict(X_test_tfidf)
                        Req_predicted = Req_clf.predict(X_test_tfidf)
#                        ReqAmdProp_predicted = ReqAmdProp_clf.predict(X_test_tfidf)
#                        ReqProp_predicted = ReqProp_clf.predict(X_test_tfidf)
#			print Req_predicted[0]
#                        print Prop_predicted[0]
#                        print Amd_predicted[0]
#			print Cmt_predicted[0]
#			print Dlv_predicted[0]
			if Req_predicted[0] == 1:
				print "It's a request!"
			if Prop_predicted[0] == 1:
				print "It's a proposition!"
                        if Req_predicted[0] == 1 or Prop_predicted[0] == 1:
                            server = jsonrpclib.Server("http://localhost:8080")

                            result = loads(server.parse(text))
#print "Result", result     
			    output = ""
			    for s in result['sentences']:
			     
                                for w in s['words']:
#				    print w
    				    if "Timex" in w[1].keys():
					output = output + " " + w[0]
    					print w[0]

				    if 'NamedEntityTag' in w[1].keys():
					if w[1]['NamedEntityTag'] == "NUMBER":
					    #time = parse(w[0])
				            print w[0]
					    output = output + w[0]
			    t_output = parse(output)
			    print t_output


#'NamedEntityTag': u'NUMBER'
				    #if ""


#			ofile.write(text+"\n")
#			print Amd_predicted[0]
#			#ofile.write(Amd_predicted)
#                        ofile.write("\n")
#			ofile.write("-----------\n")
			return "UNKNOWN"


	# This method gets the type of Piazza Email (whether it is a question, note, post or unknown)
	def getPiazzaType(self, contentText):
		contentLines = contentText.split("\n")
		piazzaType = ""
		for line in contentLines:
			if "question" in line.lower():
				piazzaType = "QUESTION"
			elif "note" in line.lower():
				piazzaType = "NOTE"
			elif "post" in line.lower():
				piazzaType = "POST"
			else:
				piazzaType = "UNKNOWN"
			return piazzaType

	# This method defines the flow of logic to get the relevant content of email depending on source
	def getRelevantContent(self, emailContent):
		if (emailContent["SENDERSOURCE"] == "PIAZZA" and emailContent["TYPE"] != "UNKNOWN"):
			return self.getPiazzaRelevantContent(emailContent["RAWCONTENT"])
		else:
			return emailContent["RAWCONTENT"]

	# This method gets the relevant content for Piazza emails
	def getPiazzaRelevantContent(self, contentText):
		contentText = contentText[contentText.index("CONTENT:"):contentText.index("Go to http")]
		# We remove the first line from the piazza email because the first line contains text such as "Your classmate posted a new question"
		sansfirstline = '\n'.join(contentText.split('\n')[1:]) 
		return sansfirstline

	# This method simply converts the dictionary into JSON and prints the final output
	def generateFinalOutputJSON(self):
		jsonarray = json.dumps(self.emailDictionary, ensure_ascii=False)
		print "{\"AllEmails\":" + jsonarray + "}"


test = EmailContent()
test.getRawText()
