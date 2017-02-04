# InMind Email Understanding

This repository has all the code of the experiments and trained models for classifying, annotating and extracting information from e-mails.

All the experiments were done using the Enron Corpus hosted by CMU's Professor William Cohen.

The main sub-projects of this project are divided as follows:

1. Text Summarizer
2. Document classifier
3. Named Entity Recognizer



### Text Summarizer

In the text summarizer we implemented an extractive method based on TextRank.

### Document Classifier

The document classifier has some methods implemented such as: Naive Bayes, SVM and FastText.

### Named Entity Recognizer

The Named entity recognition section hosts the data files used for training the models, and the code for training the NE Recognizers. We mainly used the Stanford Core NLP and SpaCy for this task.