from flask import Flask, render_template, request, Markup
import json
import requests


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
                annotations.append([word, category, score, start, end])
                #print word, category, score
        if item['slot'] == 'nell-cat':
            start = item['spanStart']
            end = item['spanEnd']
            word = sentence[start:end]
            category = item['value']
            score = float(item['confidence'])
            if score > 0.8:
                annotations.append([word, category, score, start, end])

    return annotations

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def hello():
    annotated_text = ''
    annotations = []
    if request.method == "POST":
        query_text = request.form['queryText']
        annotations = microread_nell(query_text)

        annotations = sorted(sorted(annotations, key=lambda x:x[2], reverse=True), key = lambda x:x[3])
        anno_map = dict()
        # Keep the top annotations
        for anno in annotations:
            if (anno[3], anno[4]) not in anno_map:
                anno_map[(anno[3], anno[4])] = (anno[1], anno[2])
            elif anno_map[(anno[3], anno[4])][1] < anno[2]:
                anno_map[(anno[3], anno[4])] = (anno[1], anno[2])

        annotations = [[a[0], a[1], '%.3f'%(a[2]), a[3], a[4]] for a in annotations]

        filtered_anno = []
        for key, value in anno_map.iteritems():
            start, end = key
            category, score = value
            filtered_anno.append([category, '%.3f'%(score), start, end])

        filtered_anno = sorted(filtered_anno, key=lambda x: x[2])

        offset = 0
        marked_text = query_text
        for anno in filtered_anno:
            start = anno[2]
            end = anno[3]
            sel_text = marked_text[start+offset:end+offset]
            marked_sel_text = '''<mark title="{} | {}">{}</mark>'''.format(anno[0], anno[1], sel_text)
            if start == 0:
                marked_text = marked_sel_text + marked_text[end:]
            elif end == len(marked_text)+offset:
                marked_text = marked_text[:start+offset] + marked_sel_text
            else:
                marked_text = marked_text[:start+offset] + marked_sel_text + marked_text[end+offset:]

            print marked_text
            print 'start: {}     end: {}     offset: {}'.format(start, end, offset)
            offset += len(marked_sel_text)-len(sel_text)

        annotated_text = Markup(marked_text)

    return render_template('nellDisplay.html',displayText = annotated_text, annotations=annotations)

if __name__ == '__main__':
    app.run()