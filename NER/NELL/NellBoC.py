'''
Created on Jun 29, 2016

@author: zhongzhu, salmedina
'''
import json
import requests
import os
import yaml
from NellCacheDB import *

def microread_nell(sentence):
    data = {"action": "plaindoc", "text": sentence, "format": "raw"}
    response = requests.post("http://rtw.ml.cmu.edu/rtw/api/mod2015", data=data)
    res_str = response.text

    annotations = []
    for line in res_str.split("\n"):
        item = json.loads(line)
        if item['slot'] == 'nell-ooccat':
            start = item['spanStart']
            end = item['spanEnd']
            word, category, score = item['value'].split('|')
            score = float(score)
            if score > 0.8:
                anno = {}
                anno['text'] = word
                anno['category'] = category
                anno['score'] = score
                anno['start'] = start
                anno['end'] = end
                annotations.append(anno)
                #print word, category, score
        if item['slot'] == 'nell-cat':
            start = item['spanStart']
            end = item['spanEnd']
            word = sentence[start:end]
            category = item['value']
            score = float(item['confidence'])
            if score > 0.8:
                if score > 0.8:
                    anno = {}
                    anno['text'] = word
                    anno['category'] = category
                    anno['score'] = score
                    anno['start'] = start
                    anno['end'] = end
                    annotations.append(anno)

    return annotations

def max_annotations(annotations):
    ann_map = {}
    for ann in annotations:
        query = (ann['start'], ann['end'])
        if query in ann_map:
            if ann_map[query]['score'] < ann['score']:
                ann_map[query] = ann
        else:
            ann_map[query] = ann

    # Get list out of map and sort it
    res_list = sorted(ann_map.values(), key=lambda x:x['start']) #sort by start
    return res_list

def annotation_overlap(a, b):
    if a['end'] < b['start'] or b['end'] < a['start']:
        return 0
    values = [a['end']-a['start'], a['end']-b['start'], b['end']- a['start'], b['end']-b['start']]
    return min(values)

def annotate_text(text_filename, ann_filename, cache_db, append):
    text = open(text_filename).read()

    annotations = ''
    if not cache_db.in_cache(text):
        annotations = microread_nell(text)
        cache_db.save_annotation(text, annotations)
    else:
        annotations = cache_db.get_annotation(text)

    annotations = max_annotations(annotations)

    tag_id = 1
    write_mode = 'w'
    if append:
        write_mode = 'a'
        with open(ann_filename, 'r') as ann_file:
            ann_text = ann_file.read()
            lines = ann_text.splitlines()
            tag_id = len(lines) + 1

    with open(ann_filename, write_mode) as ann_file:
        for ann in annotations:
            #0:text, 1:category, 2:score, 3:start, 4:end
            formatted_entry = '''T%d\t%s %d %d\t%s\n'''%(tag_id, 'NELL_'+ann['category'], ann['start'], ann['end'], ann['text'])
            ann_file.write(formatted_entry)
            tag_id += 1

if __name__=='__main__':
    # Instantiate the cache object
    config_filename = 'dbconfig.yaml'
    dbconfig = config = yaml.load(open(config_filename))
    cache = NellCacheDB(host=dbconfig['host'],
                        user=dbconfig['user'],
                        passwd=dbconfig['passwd'],
                        db_name=dbconfig['db'])

    # Go through all the files in the given dir
    dir_list = ['schedule/sample1', 'schedule/sample2', 'schedule/sample3']
    for data_dir in dir_list:
        for item in os.listdir(data_dir):
            if os.path.isdir(item):
                continue
            item_path = os.path.join(data_dir, item)
            item_filename, item_ext = os.path.splitext(item_path)
            if item_ext == '.txt':
                print 'Annotating %s'%(item)
                item_ann_path = item_path.replace('.txt','.ann')
                annotate_text(item_path, item_ann_path, cache, True)

