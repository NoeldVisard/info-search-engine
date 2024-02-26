from os.path import dirname, join

import nltk
import string
import re
from os import listdir, path
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from pymystem3 import Mystem

class Tokenizer:
    def __init__(self):
        self.pages_folder_name = join(dirname(__file__), '../task_1/pages')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('russian'))
        self.mystem = Mystem()
        self.tokens = set()
        self.lemmas = dict()
        self.max_word_length = 20

    def is_correct_token(self, token):
        has_punctuation = any(x in string.punctuation for x in token)
        is_stop_word = token.lower() in self.stop_words
        is_number = re.match(r'^[0-9]+$', token)
        is_russian = re.match(r'^[а-яА-Я]{2,}$', token)
        are_stuck_words = sum(map(str.isupper, token[1:])) > 0 and (
            sum(map(str.islower, token[1:])) > 0 or str.islower(token[0])
        )
        is_good_word = True
        is_good_length = len(token) <= self.max_word_length

        return not has_punctuation and not is_stop_word and not is_number and is_russian and not are_stuck_words and is_good_word and is_good_length

    def get_list_of_tokens(self):
        for page_name in listdir(self.pages_folder_name):
            with open(path.join(self.pages_folder_name, page_name), 'r', encoding='utf-8') as html:
                text = BeautifulSoup(html, features='html.parser').get_text()
                tokens = wordpunct_tokenize(text)
                self.tokens |= set(filter(self.is_correct_token, tokens))

        self.write_list_of_tokens()

    def write_list_of_tokens(self):
        with open(path.join(path.dirname(__file__), 'tokens.txt'), 'w') as tokens_file:
            tokens_file.write('\n'.join(self.tokens))

    def group_tokens_by_lemmas(self):
        for token in self.tokens:
            analysis = self.mystem.analyze(token)
            if analysis and 'analysis' in analysis[0] and analysis[0]['analysis']:
                lemma = analysis[0]['analysis'][0]['lex']
            else:
                lemma = token.lower()
            self.lemmas.setdefault(lemma, []).append(token)

        self.write_list_of_lemmas()

    def write_list_of_lemmas(self):
        with open(path.join(path.dirname(__file__), 'lemmas.txt'), 'w') as lemmas_file:
            for lemma, tokens in self.lemmas.items():
                line = f'{lemma}: {" ".join(tokens)}\n'
                lemmas_file.write(line)


if __name__ == '__main__':
    tokenizer = Tokenizer()
    tokenizer.get_list_of_tokens()
    tokenizer.group_tokens_by_lemmas()
