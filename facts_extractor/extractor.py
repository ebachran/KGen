import os

from argparse import ArgumentParser
from sys import argv
from sys import path

from facts_extractor.openie import OpenIE
from facts_extractor.srl import SemanticRoleLabeler

class FactsExtractor:

    def extract_triples(self, input_filename, openie='stanford', srl=False, depparse=False, verbose=False):
        # Convert to absolute path name
        input_filename = os.path.realpath(input_filename)

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        output_filename = os.path.splitext(input_filename)[0] + '_triples.txt'
        open(output_filename, 'w').close()

        if srl:
            output = SemanticRoleLabeler().extract(input_filename, output_filename, verbose)
        else:
            output = OpenIE(openie).extract(input_filename, output_filename, verbose)

        print('Extracted triples were stored at {}'.format(output))

        return output

def main(args):
    arg_p = ArgumentParser('python extractor.py', description='Extracts facts from an unstructured text.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-o', '--openie', type=str, default='stanford', help='Specify the openie system, e.g. stanford (default), clausie ... - Will *NOT* perform SRL!')
    arg_p.add_argument('-s', '--srl', action='store_true', help='Perform Semantic Role Labeling (SRL) - Will *NOT* perform openie!')
    arg_p.add_argument('-d', '--depparse', action='store_true', help='Perform dependency parsing to retrieve secondary facts')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    openie = args.openie
    srl = args.srl
    depparse = args.depparse
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    extractor = FactsExtractor()
    extractor.extract_triples(filename, openie, srl, depparse, verbose)

if __name__ == '__main__':
    exit(main(argv))

