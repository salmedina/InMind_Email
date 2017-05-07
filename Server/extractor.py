# python Extractor_v2.py corpusBody user
# Coded by Chen Hu and Yinzhi Yu
import sys
import re
import json
from cStringIO import StringIO
# Class State is a finite state machine for the thread and head
class State:
	# Meta state
	state_set = set(['Body','Head'])
	# Sub state in head
	headType_set = set(['Original','Forward','To','From','Email'])

	def __init__(self):
		self.state = None
		self.headType = None
		self.headEnd = None

	# transition between states, given the current text line and context
	def transition(self,line,text,lineno):
		if self.state == None or self.state == "Body":
			return self.transFromBody(line,text,lineno)
		else:
			if self.headType == "Original":
				return self.transInOrg(line,text,lineno)
			elif self.headType == "Forward":
				return self.transInFwd(line,text,lineno)
			elif self.headType == "To":
				return self.transInTo(line,text,lineno)
			elif self.headType == "From":
				return self.transInFm(line,text,lineno)
			elif self.headType == "Email":
				return self.transInEml(line,text,lineno)

	# Check if the current line is the begining of a head
	def check_head(self,line,text,lineno):
		if "--Original Message--" in line:
			self.headEnd = self.findOrgEnd(line,text,lineno)
			return 'Original'
		if "-- Forwarded by" in line:
			self.headEnd = self.findFwdEnd(line,text,lineno)
			return "Forward"
		if "To: " in line[:5]:
			self.headEnd = self.findToEnd(line,text,lineno)
			return "To"
		if "From: " in line[:8]:
			tmp = self.findFromEnd(line,text,lineno)
			if tmp == -1:
				return None
			else:
				self.headEnd = tmp
				return "From"
		if re.search('<?[^@]+@[^@]+\.[^@]+>? on [\d | /]+ [\d | :]+ [(AM) | (PM)]',line) != None :
			self.headEnd = self.findEmlEnd(line,text,lineno)
			return "Email"
		return None


	# Transition in state Body
	def transFromBody(self,line,text,lineno):
		tag = self.check_head(line,text,lineno)
		if tag != None:
			self.state = "Head"
			self.headType = tag
			return True
		else:
			self.state = "Body"
			return False

	# Transition in state Head and sub_state in Orginal
	def transInOrg(self,line,text,lineno):
		if lineno == self.headEnd:
			self.headEnd = None
			self.state = "Body"
			return True
		
		return False

	# Transition in state Head and sub_state in Forward
	def transInFwd(self,line,text,lineno):
		if lineno == self.headEnd:
			self.headEnd = None
			self.state = "Body"
			return True

		return False

	# Transition in state Head and sub_state in To
	def transInTo(self,line,text,lineno):
		if lineno == self.headEnd:
			self.headEnd = None
			self.state = "Body"
			return True
		
		return False

	# Transition in state Head and sub_state in From
	def transInFm(self,line,text,lineno):
		if lineno == self.headEnd:
			self.headEnd = None
			self.state = "Body"
			return True
		
		return False

	# Transition in state Head and sub_state in Email
	def transInEml(self,line,text,lineno):
		if lineno == self.headEnd:
			self.headEnd = None
			self.state = "Body"
			return True
		
		return False

	# Given the context, find the end line of this Forward head
	def findFwdEnd(self,line,text,lineno):
		i = lineno + 1
		from_index = 0
		while i < len(text) and (not "-- Forwarded by" in text[i]):
			if "Subject:" in text[i]:
				return i
			if "From:" in text[i]:
				from_index = i
			i += 1

		if from_index!=0:
			return from_index
		else:
			return lineno + 1

	# Given the context, find the end line of this To head
	def findToEnd(self,line,text,lineno):
		i = lineno + 1
		re_index = 0
		while i < len(text):
			if "Subject:" in text[i]:
				return i
			if "X-Mailer" in text[i]:
				return i
			if (re_index == 0) and ("Re:" in text[i]):
				re_index = i
			i += 1
		if re_index != 0:
			return re_index
		return lineno + 1

	# Given the context, find the end line of this From head
	def findFromEnd(self,line,text,lineno):
		i = lineno + 1
		sent_index = 0
		to_index = 0
		while i < len(text):
			if "Subject:" in text[i]:
				return i
			if "Re:" in text[i]:
				return i
			if "Date:" in text[i]:
				return i
			if (sent_index == 0) and ("Sent:" in text[i]):
				sent_index = i
			if (to_index ==0 ) and ("To:" in text[i]):
				to_index = i
			i += 1
		if (sent_index !=0) and (to_index != 0):
			return max(sent_index,to_index)
		else:
			return -1

	# Given the context, find the end line of this Original head
	def findOrgEnd(self,line,text,lineno):
		i = lineno + 1
		from_index = 0
		while i < len(text):
			if "Subject:" in text[i]:
				return i
			if (from_index == 0) and "From:" in text[i]:
				from_index = i
			i += 1
		if from_index != 0:
			return from_index
		else:
			return lineno + 1

	# Given the context, find the end line of this Email head
	def findEmlEnd(self,line,text,lineno):
		i = lineno + 1
		to_index = 0
		while i < len(text):
			if "Subject:" in text[i]:
				return i
			if (to_index == 0) and ("To:" in text[i]):
				to_index = i
				while i < len(text):
					if text[i] == '\n':
						to_index = i - 1
						break
					i += 1
			i += 1
		if to_index != 0:
			return to_index
		else:
			return lineno + 1


class Extractor:
	# Find some missing header lines before current line
	@staticmethod
	def popLine(i,text):
		pre = i
		while pre>=1:
			if not re.match('>*$',text[pre-1]):
				pre = pre-1
			else:
				break
		return pre

	# Extarct the header from the emial in filesName
	@staticmethod
	def extract(email_doc):
		reader = StringIO(email_doc)
		text= []
		start = []
		end = []
		length = []
		for line in reader:
			text.append(line)
			length.append(len(line))
		doc_state = State()

		i = 0
		while i<len(text):
			if doc_state.transition(text[i],text,i):
				if doc_state.state == "Head":
					if(doc_state.headType == "To" or doc_state.headType == "From"):
						startIndex = Extractor.popLine(i,text)
					else:
						startIndex = i
					start.append(startIndex)
					if i == len(text) - 1:
						end.append(i)
				else:
					end.append(i)
			i += 1

		doc = []
		thread = []
		i=0
		threadCount = 0
		charCount = 0
		for threadCount in range(len(start)):
			if start[threadCount]!=0:
				tmp = ""
				for k in range(i,start[threadCount]):
					tmp+=text[k]
				tmpCount = sum(length[0:i])
				doc.append((tmpCount, tmp))
			tmp=""
			for k in range(start[threadCount],end[threadCount]+1):
				tmp += text[k]
			tmpCount = sum(length[0:start[threadCount]])
			thread.append((tmpCount, tmp))
			i=end[threadCount]+1

		tmp=""
		for k in range(i,len(text)):
			tmp+=text[k]
		tmpCount = sum(length[0:i])
		doc.append((tmpCount, tmp))

		return (doc,thread)



	


	

	





		
