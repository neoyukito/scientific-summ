from base import Summarizer
from collections import defaultdict
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.summarizers.lex_rank import LexRankSummarizer
import itertools
from log_conf import Logger
from util.tokenization import WordTokenizer, SentTokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

logger = Logger('.'.join(__file__.split('/')[-2:-1])).logger


class Summarizer(Summarizer):
    '''
    classdocs
    '''

    def __init__(self, args, opts):
        '''
        Constructor
        '''
        self.s_t = SentTokenizer(offsets=False)
        self.w_t = WordTokenizer(stem=False)

    def summarize(self, extracted_refs, facet_results, max_length=250):
        '''
        Summarizes the extracted references based on the facet results

        Args:
            extracted_refs(list) -- results of the method.run (e.g. simple.py)
            facet_results(dict) -- facets for each extracted reference
                Look at data/task1b_results1.json
            max_length(int) -- maximum length of the summary
        '''
        summaries = defaultdict(lambda: defaultdict(list))
        for t in extracted_refs:
            topic = t[0]['topic']
            citance = t[0]['citance_number']
            if isinstance(t[0]['sentence'][0], list):
                logger.warn('Unexpected, should check')
            summaries[topic.upper()]\
                [facet_results[topic.upper()]
                 [str(citance)]['SVM_LABEL']].append([t[0]['citation_text']])

        summarizer = TextRankSummarizer(Stemmer('english'))

        final_summ = defaultdict(lambda: defaultdict(dict))
        ret_summ = defaultdict(list)
        counts = defaultdict(lambda: defaultdict(dict))
        for t in summaries:
            for facet in summaries[t]:
                if len(summaries[t][facet]) > 1:
                    summs = list(
                        itertools.chain.from_iterable(summaries[t][facet]))
                    parser = PlaintextParser.from_string(
                        ' '.join(summs), Tokenizer('english'))
                    summ = summarizer(parser.document, max_length)
                    final_summ[t][facet] = [unicode(sent) for sent in summ]
                    counts[t][facet] = len(final_summ[t][facet])
                else:
                    final_summ[t][facet] = self.s_t(summaries[t][facet][0])
            i = 0
            while self.w_t.count_words(ret_summ[t]) < max_length:
                for fct in final_summ[t]:
                    if i < len(final_summ[t][fct]):
                        ret_summ[t].append(final_summ[t][fct][i])
                i += 1
            while self.w_t.count_words(ret_summ[t]) > max_length:
                ret_summ[t].pop()


#         summ = defaultdict(list)
#         tokzer = WordTokenizer(stem=False)
#         for k in final_summ:
#             i = 0
#             while tokzer.count_words(summ[k]) < max_length:
#                 for f in final_summ[k]:
#                     if len(final_summ[k][f]) > i and\
#                             tokzer.count_words(summ[k]) < max_length:
#                         summ[k].append(final_summ[k][f][i])
        return ret_summ
