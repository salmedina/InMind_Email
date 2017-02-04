from __future__ import division
import re
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from os.path import join as join_path

# GLOBALS
MANUAL_LABELS = ['Person', 'Date', 'DateSpan', 'Time', 'TimeSpan', 'Location', 'Organization', 'Telephone', 'EventName', 'Topic']
NELL_LABEL_SET = set()

def filter_by_field(inlist, field_pos, field_value):
    '''Filters inlist for elements with field_value on the position field_pos'''
    return [x for x in inlist if x[field_pos] == field_value]

def extract_line_annotations(ann_line):
    '''Returns the annotation as a dictionary'''
    p = re.compile(r'(T\d+)\t(\w+) (\d+) (\d+)\t(.*)')
    items = p.findall(ann_line)
    if items is None or len(items) < 1:
        return None

    items = items[0]
    annotation = {}
    annotation['id'] = items[0]
    annotation['category'] = items[1]
    annotation['start'] = int(items[2])
    annotation['end'] = int(items[3])
    annotation['span'] = annotation['end'] - annotation['start']
    annotation['text'] = items[4]
    return annotation

def extract_dir_annotations(dir_path, extension):
    if not os.path.isdir(dir_path):
        return []

    annotations = []
    file_list = get_all_files_list(dir_path, extension, True)
    for ann_filepath in file_list:
        ann_text = open(ann_filepath, 'r').read();
        for ann_line in ann_text.splitlines():
            annotation = extract_line_annotations(ann_line)
            if annotation is not None:
                annotation['file'] = ann_filepath
                annotations.append(annotation)

    return annotations

def calc_overlap(a, b):
    '''a,b must be annotation dictionaries'''
    if a['end'] < b['start'] or b['end'] < a['start']:
        return 0
    values = [a['end']-a['start'], a['end']-b['start'], b['end']- a['start'], b['end']-b['start']]
    return min(values)

def extract_overlaps(ann_text, text_id):
    '''Makes a list of overlaps found within the list of annotations'''
    # get the annotations in different lists
    manual_annotations = []
    nell_annotations = []
    for line in ann_text.splitlines():
        annotation = extract_line_annotations(line)
        if annotation is not None:
            if annotation['category'].startswith('SPACY_'):
                nell_annotations.append(annotation)
            else:
                manual_annotations.append(annotation)

    # check overlaps between all annotations in brute force manner
    # TODO: improve this by advancing least cursor
    overlaps = []
    for manual_ann in manual_annotations:
        for nell_ann in nell_annotations:
            overlap_len = calc_overlap(manual_ann, nell_ann)
            if overlap_len > 0:
                # TODO: change overlaps to dictionary objects
                overlap={}
                overlap['manual_cat'] = manual_ann['category']
                overlap['nell_cat'] = nell_ann['category']
                overlap['length'] = overlap_len
                overlap['id'] = text_id
                overlaps.append(overlap)
                NELL_LABEL_SET.add(nell_ann['category'])

    return overlaps

def extract_dir_overlaps(dir_path, extension):
    if not os.path.isdir(dir_path):
        return []

    dir_overlaps = []
    file_list = get_all_files_list(dir_path, extension, True)
    for ann_filepath in file_list:
        ann_text = open(ann_filepath, 'r').read();
        dir_overlaps.append(extract_overlaps(ann_text, ann_filepath))

    dir_overlaps = flatten_list(dir_overlaps)
    return dir_overlaps

def count_overlap_spans(overlaps):
    '''overlaps is a list of overlaps and sum all the lengths'''
    return sum([x[2] for x in overlaps])

def count_total_spans(ann_text):
    manual_total_term = 0
    manual_total_span = 0
    nell_total_term = 0
    nell_total_span = 0
    for line in ann_text.splitlines():
        annotation = extract_line_annotations(line)
        if len(annotation.keys()) < 1:
            continue
        annotation_span = annotation['start'] - annotation['end']
        if annotation['category'].startswith('SPACY_'):
            nell_total_term += 1
            nell_total_span += annotation_span
        else:
            manual_total_term += 1
            manual_total_span += annotation_span

    return manual_total_span, manual_total_term, nell_total_span, nell_total_term

def count_dir_spans(dir_path, extension):
    if not os.path.isdir(dir_path):
        return []

    manual_terms=0
    manual_chars=0
    nell_terms=0
    nell_chars=0

    file_list = get_all_files_list(dir_path, extension, True)
    for ann_file_path in file_list:
        ann_text = open(ann_file_path, 'r').read();
        tmp_manual_chars, tmp_manual_terms, tmp_nell_chars, tmp_nell_terms = count_total_spans(ann_text)
        manual_terms += tmp_manual_terms
        manual_chars += tmp_manual_chars
        nell_terms += tmp_nell_terms
        nell_chars += tmp_nell_chars

    return

def flatten_list(inlist):
    return [x for sublist in inlist for x in sublist]

def build_matrix(overlap_list):
    manual_map = {}
    nell_map = {}
    idx = 0
    manual_labels_list = sorted(MANUAL_LABELS)
    nell_labels_list = sorted(list(NELL_LABEL_SET))

    for label in manual_labels_list:
        manual_map[label]=idx
        idx += 1
    idx = 0
    for label in nell_labels_list:
        nell_map[label] = idx
        idx += 1

    corr_matrix = np.zeros((len(list(NELL_LABEL_SET)), len(MANUAL_LABELS)))

    for overlap in overlap_list:
        corr_matrix[ nell_map[overlap['nell_cat']] ][ manual_map[overlap['manual_cat']]] += 1

    return corr_matrix, manual_labels_list, nell_labels_list

def plot_heatmap(data, row_labels, column_labels):

    # Plot it out
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(data, cmap=plt.cm.Blues, alpha=0.8)

    # Format
    fig = plt.gcf()
    fig.set_size_inches(8, 11)

    # turn off the frame
    ax.set_frame_on(False)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(data.shape[1]) + 0.5, minor=False)

    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    # note I could have used nba_sort.columns but made "labels" instead
    ax.set_xticklabels(column_labels, minor=False)
    ax.set_yticklabels(row_labels, minor=False)

    # rotate the
    plt.xticks(rotation=45)

    ax.grid(False)

    # Turn off all the ticks
    ax = plt.gca()

    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False

    plt.xlabel('Manual labels')
    plt.ylabel('SPACY labels')

    plt.show()

def pprint_overlaps(inlist):
    for item in inlist:
        print ", ".join(str(item[k]) for k in item.keys())

def draw_nell_histograms(target_dir, ext):
    all_annotations = extract_dir_annotations(target_dir, ext)
    all_overlaps = extract_dir_overlaps(target_dir, ext)

    nell_annotations = {}
    nell_overlaps = {}

    # Count all the annotations and overlaps
    for annotation in all_annotations:
        if annotation['category'].startswith('SPACY_'):
            if annotation['category'] not in nell_annotations:
                nell_annotations[annotation['category']] = 1
            else:
                nell_annotations[annotation['category']] += 1

    for overlap in all_overlaps:
        if overlap['nell_cat'] not in nell_overlaps:
            nell_overlaps[overlap['nell_cat']] = 1
        else:
            nell_overlaps[overlap['nell_cat']] += 1

    # Flatten dictionaries into lists for histogram
    nell_annotations_list = sorted(nell_annotations.items(), key=lambda x: x[1], reverse=True)
    all_labels, all_values = zip(*nell_annotations_list)
    all_overlap_values = []
    for label in all_labels:
        if label in nell_overlaps:
            all_overlap_values.append(nell_overlaps[label])
        else:
            all_overlap_values.append(0)

    all_labels = list(all_labels)
    all_values = list(all_values)
    all_overlap_values = list(all_overlap_values)
    all_clean_labels = [x.replace('SPACY_', '') for x in all_labels]
    draw_stacked_bars(all_clean_labels, all_values, all_overlap_values)

def draw_stacked_bars(x, y, z):
    # Plot 1 - background - "total" (top) series
    sns.set_style("whitegrid")
    sns.barplot(x=x, y=y, color="#FA6900")

    # Plot 2 - overlay - "bottom" series
    bottom_plot = sns.barplot(x=x, y=z, color="#69D2E7")

    topbar = plt.Rectangle((0, 0), 1, 1, fc="#FA6900", edgecolor='none')
    bottombar = plt.Rectangle((0, 0), 1, 1, fc='#69D2E7', edgecolor='none')
    l = plt.legend([bottombar, topbar], ['Overlapping', 'Total'], loc=1, ncol=2, prop={'size': 16})
    l.draw_frame(False)

    # Optional code - Make plot look nicer
    sns.despine(left=True)
    bottom_plot.set_ylabel("Y-axis label")
    bottom_plot.set_xlabel("X-axis label")

    # Set fonts to consistent 16pt size
    for item in ([bottom_plot.xaxis.label, bottom_plot.yaxis.label] +
                  bottom_plot.get_xticklabels() +
                  bottom_plot.get_yticklabels()):
        item.set_fontsize(8)

    plt.xticks(rotation=90)
    plt.ylabel('Frequency')
    plt.xlabel('Tag')
    plt.show()


def print_statistics(target_dir, ext):
    # Calculate the totals
    manual_total_chars, manual_total_annotations, nell_total_chars, nell_total_annotations = 0,0,0,0
    all_annotations = extract_dir_annotations(target_dir, ext)
    for annotation in all_annotations:
        if annotation['category'].startswith('SPACY_'):
            nell_total_annotations += 1
            nell_total_chars += annotation['span']
        else:
            manual_total_annotations += 1
            manual_total_chars += annotation['span']

    print "--- TOTALS ---"
    print "Total annotations:           %d" % (len(all_annotations))
    print "     SPACY                    %d" % (nell_total_annotations)
    print "     MANUAL                  %d" % (manual_total_annotations)
    print "Ratio:                       %f" % (nell_total_annotations / manual_total_annotations)
    print "--------------"
    print "Total chars:                 %d" % (nell_total_chars + manual_total_chars)
    print "     SPACY                    %d" % (nell_total_chars)
    print "     MANUAL                  %d" % (manual_total_chars)
    print "Ratio:                       %f" % (nell_total_chars / manual_total_chars)
    print ""

    # Get statistic per MANUAL LABEL
    overlap_list = extract_dir_overlaps(target_dir, ext)
    print "--- PER LABEL ---"
    for label in MANUAL_LABELS:
        label_annotations = filter_by_field(all_annotations, 'category', label)
        label_overlap = filter_by_field(overlap_list, 'manual_cat', label)
        print '%s:\t\t%.3f' % (label, len(label_overlap) / len(label_annotations))

def get_all_files_list(dir_path, ext, recursive):
    file_list = []

    for item in os.listdir(dir_path):
        item_path = join_path(dir_path, item)
        if os.path.isdir(item_path):
            if recursive:
                dir_files = get_all_files_list(item_path, ext, True)
                file_list += dir_files
        elif os.path.isfile(item_path) and item_path.endswith(ext):
            file_list.append(item_path)

    return file_list

def main():
    # Label formatting
    target_dir = '/Users/zal/CMU/InMind/Devel/Schedule/schedule'
    overlaps = extract_dir_overlaps(target_dir, '.ann')
    corr_data, manual_labels, nell_labels = build_matrix(overlaps)
    nell_labels = [x.replace('SPACY_','') for x in nell_labels]  # Clean for visibility

    # Basic Statistics
    print_statistics(target_dir, '.ann')

    # Heatmap visualization
    pprint_overlaps(overlaps)
    plot_heatmap(corr_data, nell_labels, manual_labels)

if __name__=='__main__':
    main()
    draw_nell_histograms('/Users/zal/CMU/InMind/Devel/Schedule/schedule', '.ann')