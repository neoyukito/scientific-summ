from base import Summarizer
from collections import defaultdict
from log_conf import Logger
from util.tokenization import WordTokenizer, SentTokenizer, Utils
import random
from copy import deepcopy

logger = Logger('.'.join(__file__.split('/')[-2:-1])).logger


class Summarizer(Summarizer):
    '''
    classdocs
    '''

    def __init__(self, args, opts):
        '''
        Constructor
        '''
        self.tkzr = WordTokenizer(stem=False)
        self.s_t = SentTokenizer(offsets=False)
        self.util = Utils()

    def summarize(self, extracted_refs, facet_results, max_length=250):
        '''
        Summarizes the extracted references naively

        Randomly selects references

        Args:
            extracted_refs(list) -- results of the method.run (e.g. simple.py)
            facet_results(dict) -- facets for each extracted reference
                Look at data/task1b_results1.json
            max_length(int) -- maximum length of the summary
        '''
        summaries = defaultdict(list)
        for t in extracted_refs:
            topic = t[0]['topic']
            citance = t[0]['citance_number']
            if isinstance(t[0]['sentence'][0], list):
                logger.warn('Unexpected, should check')
            summaries[topic.upper()].extend(
                self.s_t((t[0]['sentence'])))
        summ = defaultdict(list)

        def get_summ(lst, max_length, tkzr):
            res = []
            for c in lst:
                res.append(c)
                if tkzr.count_words(res) > max_length:
                    res.pop()
                    return res
            return res

        return {k: get_summ(summaries[k], max_length, self.tkzr)
                for k in summaries}
