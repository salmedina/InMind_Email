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
This is a bad script where we first train out of main scope the NER
Then we call it from the function spacy_annotate
The correct way of doing it is:

1. Train the NER
2. Annotate the text
3. Make the overlap analysis
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

def load_model(nlp, model_dir):
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


def annotation_overlap(a, b):
    '''Calculates the total overlap of terms'''
    if a['end'] < b['start'] or b['end'] < a['start']:
        return 0
    values = [a['end']-a['start'], a['end']-b['start'], b['end']- a['start'], b['end']-b['start']]
    return min(values)

def annotate_text(text_filename, ann_filename, append):
    '''
    This function annotates the text and adds the annotations made by SpaCy to the corresponding ann file
    @text_filename : the text file path
    @ann_filename : the annotation file path
    @append : if the annotations should be appended to the annotation file or overwritten
    '''

    # Open TEXT file
    text = open(text_filename).read()
    # Get the annotations from SpaCy
    annotations = spacy_annotate(text)

    # If the annotations need to be appended then get the next annotation tag id
    tag_id = 1
    write_mode = 'w'
    if append:
        write_mode = 'a'
        with open(ann_filename, 'r') as ann_file:
            ann_text = ann_file.read()
            lines = ann_text.splitlines()
            tag_id = len(lines) + 1

    # for each annotation, get the formatted line and add it to file according to the append option
    with open(ann_filename, write_mode) as ann_file:
        for ann in annotations:
            '''
            ANN fileds format
            0:text, 1:category, 2:score, 3:start, 4:end
            '''
            formatted_entry = '''T%d\t%s %d %d\t%s\n'''%(tag_id, 'SPACY_'+ann['category'], ann['start'], ann['end'], ann['text'].replace('\n',''))
            ann_file.write(formatted_entry)
            tag_id += 1

def run_experiment():
    # Go through all the files in the given dir
    dir_list = ['schedule/sample1', 'schedule/sample2', 'schedule/sample3']
    for data_dir in dir_list:
        # For each of the items in the directories
        for item in os.listdir(data_dir):
            if os.path.isdir(item):  # Ignore if it is a directory
                continue
            # Go through the txt files and get the ann filepath
            item_path = os.path.join(data_dir, item)
            item_filename, item_ext = os.path.splitext(item_path)
            if item_ext == '.txt':
                print 'Annotating %s' % (item)
                item_ann_path = item_path.replace('.txt', '.ann')
                annotate_text(item_path, item_ann_path, True)

def run_training():
    print ""
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
        print 'Saving the model to ./ner'
        save_model(ner, './ner')
    else:
        print 'The model could not be built'

if __name__=='__main__':
    #run_experiment()
    run_training()