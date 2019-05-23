import os

from argparse import ArgumentParser
from sys import argv
from sys import path

path.insert(0, '../')
from common.babelfy.babelfywrapper import BabelfyWrapper
from common.ncbo.ncbowrapper import NCBOWrapper

class Linker:

    def link(self, input_filename, k_base=None, verbose=False):
        if not input_filename.startswith('/'):
            input_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + input_filename

        print('Processing text from {} \nPlease wait, as it may take a while ...'.format(input_filename))

        with open(input_filename, 'r') as input_file:
            contents = input_file.read()
            input_file.close()

        linked = {}
        if k_base is None:
            linked.update(self.__babelfy(contents, verbose))
        else:
            k_bases = k_base.split(',')
            for base in k_bases:
                if base == 'babelfy':
                    linked.update(self.__babelfy(contents, verbose))
                elif base == 'ncbo':
                    linked.update(self.__ncbo(contents, verbose))
                else:
                    raise Exception("Unknown knowledge base!")

        output_filename = os.path.splitext(input_filename)[0] + '_links.txt'
        open(output_filename, 'w').close() # Clean the file in case it exists

        with open(output_filename, 'a') as output_file:
            for key in linked.keys():
                output_file.write(key.encode('utf-8') + ';' + linked[key] + '\n')
            output_file.close()
        print('Linked entities and concepts were stored at {}'.format(output_filename))

        return output_filename

    def __babelfy(self, contents, verbose=False):
        if verbose:
            print('Searching for entities, concepts and their links, using the Babelfy base')

        babelfy = BabelfyWrapper()
        disambiguated = babelfy.disambiguate(contents)

        links = {}
        for disambiguation in disambiguated:
            entity = BabelfyWrapper.frag(disambiguation, contents).upper()
            uri = disambiguation.babelnet_url()#disambiguation.babel_synset_id()#

            if verbose:
                print('Mapped "{}" to {}'.format(entity, uri))
                disambiguation.pprint()
            links[entity] = uri

        return links

    def __ncbo(self, contents, verbose=False):
        if verbose:
            print('Searching for entities, concepts and their links, using the NCBO base')

        ncbo = NCBOWrapper()
        annotated = ncbo.annotate(contents, ontologies='NCIT')

        links = {}
        for annotation in annotated:
            annotated_class = annotation['annotatedClass']
            if not ('prefLabel' in annotated_class and '@id' in annotated_class):
                continue

            pref_label = annotated_class['prefLabel']
            uri = annotated_class['@id']

            try:
                pref_map_str = '{}. PrefLabel: {}'.format(uri, pref_label)
            except UnicodeEncodeError:
                continue # NCBO may present some Chinese characters. We will ignore them.

            for class_annotation in annotation['annotations']:
                entity = class_annotation['text'].upper()

                if verbose:
                    print('Mapped "{}" to {}'.format(entity, pref_map_str))
                links[entity] = uri

        return links

def main(args):
    arg_p = ArgumentParser('python linker.py', description='Links the text entities to URIs from a knowledge base.')
    arg_p.add_argument('-f', '--filename', type=str, default=None, help='Text file')
    arg_p.add_argument('-k', '--kgbase', type=str, default=None, help='Knowledge base to be used, e.g. babelfy (default) or ncbo')
    arg_p.add_argument('-v', '--verbose', action='store_true', help='Prints extra information')

    args = arg_p.parse_args(args[1:])
    filename = args.filename
    kg_base = args.kgbase
    verbose = args.verbose

    if filename is None:
        print('No file provided.')
        exit(1)

    linker = Linker()
    linker.link(filename, kg_base, verbose)

if __name__ == '__main__':
    exit(main(argv))
