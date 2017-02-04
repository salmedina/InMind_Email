import os
import csv
import spacy
from spacy.gold import GoldParse
from spacy.vocab import Vocab
from spacy.pipeline import EntityRecognizer
from spacy.tokens import Doc
import random
import glob

'''
This is a bad script where we first train out of main scope the NER
Then we call it from the function spacy_annotate
The correct way of doing it is:

1. Train the NER
2. Annotate the text
3. Make the overlap analysis

Requirements for each step:

1.

'''

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


txt_ext = '.txt'
ann_ext = '.ann'
data_path = '/Users/zal/CMU/InMind/data/schedule'


print "Training SpaCy"
train_data, entity_set, event_set = build_training_list(data_path)
nlp = spacy.load('en')
ner = EntityRecognizer(nlp.vocab, entity_types=list(entity_set))

for itn in range(10):
    random.shuffle(train_data)
    for raw_text, entity_offsets in train_data:
        doc = nlp.make_doc(raw_text)
        gold = GoldParse(doc, entities=entity_offsets)

        nlp.tagger(doc)
        ner.update(doc, gold)

ner.model.end_training()

def spacy_annotate(text):
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

if __name__=='__main__':
    # Go through all the files in the given dir
    dir_list = ['schedule/sample1', 'schedule/sample2', 'schedule/sample3']
    for data_dir in dir_list:
        # For each of the items in the directories
        for item in os.listdir(data_dir):
            if os.path.isdir(item): #Ignore if it is a directory
                continue
            # Go through the txt files and get the ann filepath
            item_path = os.path.join(data_dir, item)
            item_filename, item_ext = os.path.splitext(item_path)
            if item_ext == '.txt':
                print 'Annotating %s'%(item)
                item_ann_path = item_path.replace('.txt','.ann')
                annotate_text(item_path, item_ann_path, True)

