from pycorenlp import StanfordCoreNLP
import MySQLdb, MySQLdb.cursors
import os
import json
import random
import pathlib
import spacy
from spacy.pipeline import EntityRecognizer
from spacy.gold import GoldParse

class SpaCyNER:

    def __init__(self, model_dir = None):
        if model_dir == None:
            self.nlp = spacy.load('en')
            self.ner = None
        else:
            self.nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)
            self.ner = self.load_ner(self.nlp, model_dir)


    # exclusive prefix sum for words array
    @staticmethod
    def accumu(lis):
        total = 0
        for x in lis:
            yield total
            total += (x + 1)
    
    # Get positions given lens and starts
    @staticmethod
    def get_position(lens,starts):
        for (s,l) in zip(starts,lens):
            yield (s, s+l)
    
    
    # Build the training data
    @staticmethod
    def build_training_data(num):
        try:
            db = MySQLdb.connect(host='holbox.lti.cs.cmu.edu',
                                 user='inmind',
                                 passwd='yahoo',
                                 db='enron_experiment',
                                 cursorclass=MySQLdb.cursors.SSCursor)
    
        except Exception, e:
            print 'ERROR: while connecting to database'
            print e.message
            exit()
    
        cursor = db.cursor()
    
        nlp = StanfordCoreNLP('http://localhost:9000')
    
        get_sql = "SELECT id, body_text FROM schedule_threads WHERE id = {}"
    
        step = int(600000 / num)
        count = 0
    
        try:
            mid = 1
            cursor.execute(get_sql.format(mid))
            rows = cursor.fetchall()
    
            training_list = []
            entity_set = set();
    
            while len(rows) > 0:
                row = rows[0]
                if row[1] != None:
                    res = nlp.annotate(row[1],
                                       properties={
                                           'annotators': 'ner',
                                           'outputFormat': 'json',
                                           'timeout': 10000,
                                       })
                    # text = '\n'.join(reduce(lambda x, y: x + [' '.join(map(lambda t: t['lemma'],y['tokens']))],res['sentences'],[]))
                    # nes = '\n'.join(reduce(lambda x, y: x + [' '.join(map(lambda t: t['ner'],y['tokens']))],res['sentences'],[]))
    
                    # text = reduce(lambda x, y: x + map(lambda t: t['lemma'],y['tokens']),res['sentences'],[])
                    if not isinstance(res, dict):
                        try:
                            res = json.loads(res.decode('utf-8') , encoding='utf-8', strict=False)
                        except ValueError:
                            print str(mid) + " time out!"
    
                            mid += 1
                            cursor.execute(get_sql.format(mid))
                            rows = cursor.fetchall()
                            continue
    
                    #positions = reduce(
                    #    lambda x, y: x + map(lambda t: (t['characterOffsetBegin'], t['characterOffsetEnd']), y['tokens']),
                    #    res['sentences'], [])
                    words = reduce(lambda x, y: x + map(lambda t: t['word'], y['tokens']), res['sentences'], [])
                    nes = reduce(lambda x, y: x + map(lambda t: t['ner'], y['tokens']), res['sentences'], [])
                    text = ' '.join(words)
                    if not isinstance(text, unicode):
                        #text = unicode(text,encoding="utf-8")
                        mid += 1
                        cursor.execute(get_sql.format(mid))
                        rows = cursor.fetchall()
                        continue
                    lengths = map(lambda x:len(x), words)
                    starts = SpaCyNER.accumu(lengths)
                    positions = list(SpaCyNER.get_position(lengths, starts))
    
    
                    annotations = []
    
                    idx = 0
                    while idx < len(nes):
                        if (nes[idx] == 'O'):
                            idx += 1
                            continue
                        entity_set.add(nes[idx])
                        end = idx + 1
                        while end < len(nes) and nes[end] == nes[idx]:
                            end += 1
                        annotations.append((positions[idx][0], positions[end - 1][1], nes[idx]))
                        idx = end
    
                    training_list.append((text, annotations))
    
                count += 1
    
                if count % 100 == 0:
                    print str(count) + " complete!"
                if count == num:
                    break
    
                mid += step
                cursor.execute(get_sql.format(mid))
                rows = cursor.fetchall()
        except MySQLdb.Error:
            print "Error: Read row Error\n"
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()
    
        return training_list, entity_set
    
    # Train the model given the training data and entity list
    @staticmethod
    def train_spacy_ner(nlp, train_data, entity_types):
        '''
        Trains a NER
        :param nlp: Spacy NLP pipeline to be used with the NER
        :param train_data: list of tuples (text, annotation_list) where the annotation_list is a list of tuples (start, end, tag) tag is a string
        :param entity_types: the possible tags for our NER
        :return: trained Spacy NER model
        '''
        # Add new words to vocab.
        for raw_text, _ in train_data:
            doc = nlp.make_doc(raw_text)
            for word in doc:
                _ = nlp.vocab[word.orth]
    
        # Train NER.
        ner = EntityRecognizer(nlp.vocab, entity_types=entity_types)
        for itn in range(5):
            random.shuffle(train_data)
            for raw_text, entity_offsets in train_data:
                doc = nlp.make_doc(raw_text)
                gold = GoldParse(doc, entities=entity_offsets)
                ner.update(doc, gold)
        return ner
    
    # A simple test for the trained ner model
    @staticmethod
    def test_training(nlp, ner):
        test_str = u'''Hello Sarah, let's meet tomorrow at 5:00 PM in the cafe next to the office'''
        test_doc = nlp.make_doc(test_str)
        nlp.tagger(test_doc)
        ner(test_doc)
        for word in test_doc:
            #print(word.text, word.orth, word.lower, word.tag_, word.ent_type_, word.ent_iob)
            print(word.text, word.ent_type_)
    
    # Save the model into path
    @staticmethod
    def save_model(ner, model_dir):
        '''
        Saves a model into local disk
        :param ner: Spacy ner model to be saved
        :param model_dir: directory path where the model will be saved
        :return: None
        '''
        # Make sure the saving path exists
        model_dir = pathlib.Path(model_dir)
        if not model_dir.exists():
            model_dir.mkdir()
        assert model_dir.is_dir()
    
        # Save the config file
        with (model_dir / 'config.json').open('wb') as file_:
            data = json.dumps(ner.cfg)
            if isinstance(data, unicode):
                data = data.encode('utf8')
            file_.write(data)
        # Save the binary model
        ner.model.dump(str(model_dir / 'model'))
        # Save the NER vocabulary: lexemes and strings
        if not (model_dir / 'vocab').exists():
            (model_dir / 'vocab').mkdir()
        ner.vocab.dump(str(model_dir / 'vocab' / 'lexemes.bin'))
        with (model_dir / 'vocab' / 'strings.json').open('w', encoding='utf8') as file_:
            ner.vocab.strings.dump(file_)

    @staticmethod
    def run_training(save_path, sample_num):
        print '___TRAINING___'
        # Instantiate the English NLP pipeline
        print 'Loading the SpaCy English pipeline'
        nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)
    
        # Get the training data from our annotations
        print 'Building the training data'
    
        train_data, entity_set = SpaCyNER.build_training_data(sample_num)
        print entity_set
    
        # Train the NER with our annotations
        print 'Training the SpaCy NER'
        ner = SpaCyNER.train_spacy_ner(nlp, train_data, list(entity_set))
    
        # Test the trained NER and save the models
        if ner is not None:
            print 'Testing the trained NER'
            SpaCyNER.test_training(nlp, ner)
            print 'Saving the model to', save_path
            SpaCyNER.save_model(ner, save_path)
        else:
            print 'The model could not be built'
    
    
    def load_ner(self, nlp, model_dir):
        '''
        Loads the NER model located in model_dir
        :param nlp: Spacy NLP pipeline to be used with the NER
        :param model_dir: path of the directory where the NER model was saved
        :return: NER model
        '''
        #nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)
        vocab_dir = pathlib.Path(os.path.join(model_dir, 'vocab'))
        with (vocab_dir / 'strings.json').open('r', encoding='utf8') as file_:
            nlp.vocab.strings.load(file_)
        nlp.vocab.load_lexemes(vocab_dir / 'lexemes.bin')
        ner = EntityRecognizer.load(pathlib.Path(model_dir), nlp.vocab, require=True)
        return ner
    

    def run_testing(self, save_path):
        print '__TESTING__'
        print 'Loading the SpaCy English pipeline'
        loading_test_nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)
        loading_test_ner = self.load_ner(loading_test_nlp, save_path)
        self.test_training(loading_test_nlp, loading_test_ner)


    def test(self, doc_body):
        if not isinstance(doc_body,unicode):
            doc_body = unicode(doc_body,'unicode-escape')
        doc = self.nlp.make_doc(doc_body)
        self.nlp.tagger(doc)
        if self.ner == None:
            self.nlp.parser(doc)
            self.nlp.entity(doc)
        else:
            self.ner(doc)
        annotations = []
        for word in doc:
            annotations.append((word.text, word.ent_type_))
        return annotations






