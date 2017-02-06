import argparse
import fasttext
import unicodedata

def unicode_to_str(in_str):
    return unicodedata.normalize('NFKD', in_str).encode('ascii','ignore')

def train_model(input_path, name, prefix):
    model = fasttext.supervised(input_path, name, label_prefix=prefix)
    return model

def test_model(model, test_path):
    test_file = open(test_path)
    test_samples = test_file.readlines()
    output = model.predict_proba(test_samples)
    return output

def write_output(output, output_path):
    output_file = open(output_path, 'w')
    formatted_output = []
    for item in output:
        out_str = ''
        if len(item)>0:
            item = item[0]
            out_str = '%s,%f\n'%(unicode_to_str(item[0]), item[1])
        else:
            out_str = '-1,0\n'
        output_file.write(out_str)
    output_file.close()

def run_experiment(input_path, prefix, name, test_path, output_path):
    '''
    This is the main entry function of the program which:
        1. trains a supervised classification model
        2. tests it
        3. writes the classification result in the output file
    '''
    model = train_model(input_path, prefix, name)
    output = test_model(model, test_path)
    write_output(output, output_path)


def ParseEntry():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', '--input', help='path to train data', required=True)
    parser.add_argument('-n', '--name', help='name of the model to be stored', required=False)
    parser.add_argument('-p', '--prefix', help='prefix to the data labels', required=False)
    parser.add_argument('-t', '--test', help='path to test data', required=True)
    parser.add_argument('-o', '--output', help='path to output file with test classifications', required=True)
    args = vars(parser.parse_args())
    return args

if __name__=='__main__':
    args = ParseEntry()

    # Fill up default values of
    if 'name' not in args.keys():
        args['name'] = 'ft_model'
    if 'prefix' not in args.keys():
        args['prefix'] = '__label__'

    run_experiment(args['input'], args['name'], args['prefix'], args['test'], args['output'])