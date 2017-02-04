from nltk.tag import StanfordNERTagger
from textblob import TextBlob

'''
SCNLP NER Annotator
Usage:
    1. Init the instance with the jar files for the SCNLP NER and Classifier
    2. Call the annotate_text method
'''

class ScnlpNerAnnotator:
    def __init__(self, scnlpNerJar, scnlpClfJar):
        self.ScnlpNerJar = scnlpNerJar
        self.ScnlpClfJar = scnlpClfJar
        self.tagger = self.build_scnlp_tagger(scnlpNerJar, scnlpClfJar)
        # Global constants for annotations
        self.ID, self.TEXT, self.LABEL, self.START, self.END = range(5)

    def join_ner_tags(self, tag1, tag2):
        joint_id    = tag2[self.ID]
        joint_text  = tag1[self.TEXT] + tag2[self.TEXT]
        joint_label = tag1[self.LABEL]
        joint_start = tag1[self.START]
        joint_end   = tag2[self.END]
        return (joint_id, joint_text, joint_label, joint_start, joint_end)

    def compress_ner_tags(self, tags):
        compressed_list = []
        last_tag = None
        for i in range(len(tags)):
            if last_tag is None:
                last_tag = tags[i]
            else:
                if tags[i][self.ID] == last_tag[self.ID]+1 and tags[i][self.LABEL] == last_tag[self.LABEL]:
                    last_tag = self.join_ner_tags(last_tag, tags[i])
                else:
                    compressed_list.append(last_tag)
                    last_tag = tags[i]
        # What remained in the accumulator
        if last_tag is not None:
            compressed_list.append(last_tag)

        return compressed_list

    def export_to_annotation(self, tags, text):
        annotations = []
        for tag in tags:
            anno = {}
            anno['text'] = text[tag[self.START]:tag[self.END]+1].replace('\n','')
            anno['category'] = tag[self.LABEL]
            anno['score'] = 1.0
            anno['start'] = tag[self.START]
            anno['end'] = tag[self.END]
            annotations.append(anno)

        return annotations

    def build_scnlp_tagger(self, jarfile, modelfile):
        return StanfordNERTagger(model_filename=modelfile, path_to_jar=jarfile)

    def annotate_text(self, text):
        '''Enters text, output list of annotations
            Annotation definition is a dict with the following fields
            anno['text']
            anno['category']
            anno['score']
            anno['start']
            anno['end']
        '''

        # Tokenize and INDEX the text
        blob = TextBlob(text)
        word_index = []
        latest_index = 0
        for w in blob.words:
            word_start = text.find(w, latest_index)
            word_end = word_start + len(w) - 1
            latest_index = word_end + 1
            word_index.append((word_start, word_end))
            #print '%s\t%d\t%d' % (w, word_start, word_end)
        words_start, words_end = zip(*word_index)

        # NER-TAG the words
        words, word_tags = zip(*self.tagger.tag(blob.words))
        ner_tags = [x for x in zip(range(len(words)), words, word_tags, words_start, words_end) if x[self.LABEL] != 'O']

        compressed_ner_list = self.compress_ner_tags(ner_tags)
        annotations = self.export_to_annotation(compressed_ner_list, text)

        return annotations

def main():
    text = '''Dear Mr. Ray,

    I regret to inform you that due to very heavy workload we cannot attend
    the Power Systems Engineering Research Center's
    upcoming Industrial Advisory Board meeting in Oak Brook.

    Our  work load does not leave us much time to get involved
    with PSERC at this moment. We would very much like to stay
    in touch and plan to reconsider our decision in the second half of this
    year.

    Vince Kaminski'''


    jarfile = '/Users/zal/CMU/InMind/Tools/stanford-ner-2015-12-09/stanford-ner.jar'
    modelfile = '/Users/zal/CMU/InMind/Tools/stanford-ner-2015-12-09/classifiers/english.muc.7class.distsim.crf.ser.gz'

    scnlpTagger = ScnlpNerAnnotator(jarfile, modelfile)

    for anno in scnlpTagger.annotate_text(text):
        print anno


if __name__=='__main__':
    main()
