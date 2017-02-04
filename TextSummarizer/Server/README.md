 # Text Summarizer Server

 This project is formed by 3 different files:

 1. TextSummarizer.py
 2. TextSummarizerServer.py
 3. TextSummarizerClient.py

 ## TL;DR:

 Start the service on the desired IP and port:
 ```
    python TextSummarizerServer -ip 127.0.0.1 -p 5000
 ```
 ```
    python TextSummarizerClient
 ```
 Sit and watch.

 ## TextSummarizer.py
 This is the core of the summarizer which is called by the server
 The summaries are extractive and therefore the resulting summary is a list of ranked sentences.

 ## TextSummarizerServer.py
 The service runs as a Flash App and therefore Flask and Jinja2 must be installed in order to have it running.
 The expected message is a string with a json message that has:

 1. body
 2. subject

 As a results it returns a summary in the following JSON format:

 - sentences[]
    - sentence
    - score

 ### Usage
 To start the service it must be called as follows:
 ```
 python TextSummarizerServer -ip 127.0.0.1 -p 5000
 ```
 You will see that the server is running and is ready to be used.

 ## TextSummarizerClient.py
 This file contains a class which is fairly easy to use as it only needs
 to be initialized with the server's IP and port
 Then the service is called by calling the method summarize.

 ```
 client = TextSummarizeClient('localhost', 5000)
 summary = client.summarize(subject, text)
 ```

 The returned summary is a list of dictionaries with the following fields:

 1. score (ranker score)
 2. sentence (sentence)

 The sentences are sorted according to the score in descending order.

