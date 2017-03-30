#!/usr/local/bin/python
import os
import csv
import json
import random
import glob
import pathlib
import spacy
from spacy.pipeline import EntityRecognizer
from spacy.gold import GoldParse
from spacy.tagger import Tagger

'''
This is an example on how to train a Spacy NER model and how to load it
'''

# GLOBALS (bad practice, I know)
txt_ext = '.txt'
ann_ext = '.ann'
data_path = '/Users/zal/CMU/InMind/data/schedule'

def build_training_list(data_dir):
    '''The resulting training data is a list of tuples
    where each tuple has (text, annotations) where annotations
    is a list of tuples (start, end, tag)'''
    entity_set = set()
    event_set = set()
    training_list = []
    # Go through all the files
    for txt_file in glob.glob(os.path.join(data_path, '*.txt')):
        # Verify annotation file exists
        ann_file = os.path.splitext(txt_file)[0] + ann_ext
        if not os.path.isfile(ann_file):
            continue
            # For each file grab the text from the txt file
        text = open(txt_file).read().decode('utf-8')

        # and grab the annotations from the ann file
        ann_list = list(csv.reader(open(ann_file, 'rb'), delimiter='\t'))

        # For each annotation
        annotations = []
        for ann_item in ann_list:
            # Grab the second element, split by spaces
            ann_fields = ann_item[1].split(' ')
            # Arrange into training tuple
            ann_start = int(ann_fields[1])
            ann_end = int(ann_fields[-1])
            ann_tag = ann_fields[0].upper()
            annotations.append((ann_start, ann_end, ann_tag))
            entity_set.add(ann_tag)
            # DEBUG: DELETE
            if ann_tag == 'EVENTNAME':
                event_set.add(ann_item[2])

        training_list.append((text, annotations))

    return training_list, entity_set, event_set


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

def load_ner(nlp, model_dir):
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

def test_training(nlp, ner):
    test_str = u'''Hello Sarah, let's meet tomorrow at 5:00 PM in the cafe next to the office'''
    test_doc = nlp.make_doc(test_str)
    nlp.tagger(test_doc)
    ner(test_doc)
    for word in test_doc:
        #print(word.text, word.orth, word.lower, word.tag_, word.ent_type_, word.ent_iob)
        print(word.text, word.ent_type_)

def spacy_annotate(nlp, text):
    annotations = []

    doc = nlp(text.decode('utf-8'))
    #ner(doc)
    for ent in doc.ents:
        anno = {}
        anno['text'] = ent.text
        anno['category'] = ent.label_
        anno['score'] = ent.vector_norm
        anno['start'] = ent.start
        anno['end'] = ent.end
        annotations.append(anno)

    return annotations

def run_training(save_path):
    print '___TRAINING___'
    # Instantiate the English NLP pipeline
    print 'Loading the SpaCy English pipeline'
    nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)

    # Get the training data from our annotations
    print 'Building the training data'
    train_data, entity_set, event_set = build_training_list(data_path)  # Extract the training data

    # Train the NER with our annotations
    print 'Training the SpaCy NER'
    ner = train_spacy_ner(nlp, train_data, list(entity_set))

    # Test the trained NER and save the models
    if ner is not None:
        print 'Testing the trained NER'
        test_training(nlp, ner)
        print 'Saving the model to', save_path
        save_model(ner, save_path)
    else:
        print 'The model could not be built'

def run_testing(save_path):
    print '__TESTING__'
    print 'Loading the SpaCy English pipeline'
    loading_test_nlp = spacy.load('en', parser=False, entity=False, add_vectors=False)
    loading_test_ner = load_ner(loading_test_nlp, save_path)
    test_training(loading_test_nlp, loading_test_ner)

if __name__=='__main__':
    run_training('ner')
    run_testing('ner')