from sys import path

path.insert(0, '../')
from common.nlputils import NLPUtils
from common.senna.sennawrapper import SennaWrapper
from common.triple import Triple

class SemanticRoleLabeler:

    def extract(self, input_filename, output_filename, verbose=False):
        return self.__senna(input_filename, output_filename, verbose)

    def __senna(self, input_filename, output_filename, verbose=False):
        if verbose:
            print('Performing Sentence Role Labeling with SENNA...')

        senna = SennaWrapper()

        out_contents = ''
        with open(input_filename, 'r') as input_file:
            sentence_number = 0
            for line in input_file.readlines():
                if len(line) < 1:
                    continue

                dependency_list = NLPUtils.dependency_parse(line, deps_key='enhancedPlusPlusDependencies', verbose=verbose)

                previous_term = ''
                previous_compound = ''
                dict_basic_to_most_specific = {}
                connective_dependencies = []
                while len(dependency_list) > 0:
                    elem = dependency_list.pop()

                    if elem[1] in ['ROOT', 'punct', 'det'] or 'subj' in elem[1] or 'obj' in elem[1]:
                        continue

                    if elem[1] in ['compound', 'nmod:poss', 'aux', 'neg'] or elem[1].endswith('mod'):
                        if previous_term == elem[0]:
                            updated_term = '{} {}'.format(elem[2], previous_compound)
                        else:
                            updated_term = '{} {}'.format(elem[2], elem[0])
                            previous_compound = elem[0]
                        dict_basic_to_most_specific[elem[0]] = updated_term

                        triple = Triple(sentence_number, updated_term, 'rdfs:subClassOf', previous_compound)

                        previous_compound = updated_term
                        previous_term = elem[0]

                        if verbose:
                            print(triple.to_string())

                        out_contents += triple.to_string() + '\n'

                    elif elem[1] in ['acl', 'appos'] or elem[1].startswith('nmod:'):
                        connective_dependencies.append(elem)

                while len(connective_dependencies) > 0:
                    elem = connective_dependencies.pop()

                    if elem[1] == 'nmod:poss':
                        continue

                    if elem[1].find(':') > 0: # e.g. 'nmod:of'
                        connector = elem[1][elem[1].find(':')+1:]
                    elif elem[1] in ['acl', 'appos']:
                        connector = ''
                    else:
                        connector = elem[1]

                    first = elem[0]
                    if first in dict_basic_to_most_specific.keys():
                        first = dict_basic_to_most_specific[first]

                    second = elem[2]
                    if second in dict_basic_to_most_specific.keys():
                        second = dict_basic_to_most_specific[second]

                    if connector == '':
                        full = '{} {}'.format(first, second)
                    else:
                        full = '{} {} {}'.format(first, connector, second)
                    
                    triple = Triple(sentence_number, full, 'local:{}_{}'.format(connector, second.replace(' ', '')), first)
                    if verbose:
                        print(triple.to_string())
                    out_contents += triple.to_string() + '\n'

                    triple = Triple(sentence_number, full, 'local:{}_{}'.format(first.replace(' ', ''), connector), second)
                    if verbose:
                        print(triple.to_string())
                    out_contents += triple.to_string() + '\n'

                    dict_basic_to_most_specific[elem[0]] = full

                senna_output = senna.srl(line, verbose=False)
                for predicate in senna_output.keys():
                    pred_args = senna_output[predicate]
                    pred_arg_names = NLPUtils.get_verbnet_args(predicate, verbose=True)
                    if len(pred_arg_names) < 1:
                        print('WARNING -- Unable to retrieve predicate arg names for "{}"'.format(predicate))

                    if verbose:
                        print('predicate: {}, args: {}'.format(predicate, pred_args))

                    for pred_arg in pred_args:
                        if 'AM-NEG' == pred_arg:
                            predicate = 'not {}'.format(predicate)
                        elif 'AM-MOD' == pred_arg:
                            predicate = ' '.join([pred_args['AM-MOD'].strip(), predicate])
                        elif pred_arg.startswith('AM-'):
                            # Remove initial stopwords (e.g. determiners)
                            s = pred_args[pred_arg].strip()
                            split = s.split(' ', 1)
                            if NLPUtils.is_stopword(split[0]) and len(split) > 1:
                                s = s.split(' ', 1)[1]

                            triple = Triple(sentence_number, predicate, 'local:{}'.format(pred_arg), s)
                            if verbose:
                                print(triple.to_string())

                            out_contents += triple.to_string() + '\n'

                    for i in range(len(pred_arg_names)):
                        pred_args_index = 'A{}'.format(i)
                        if pred_args_index in pred_args:
                            # Remove initial stopwords (e.g. determiners)
                            s = pred_args[pred_args_index].strip()
                            split = s.split(' ', 1)
                            if NLPUtils.is_stopword(split[0]) and len(split) > 1:
                                s = s.split(' ', 1)[1]

                            triple = Triple(sentence_number, predicate, 'vn.role:{}'.format(pred_arg_names[i]), s)
                            if verbose:
                                print(triple.to_string())

                            out_contents += triple.to_string() + '\n'

                sentence_number += 1

            input_file.close()

        with open(output_filename, 'w') as output_file:
            output_file.write(out_contents)
            output_file.close()

        return output_filename
