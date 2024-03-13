import re
from os.path import dirname, join
import spacy
from os import listdir, path
from bs4 import BeautifulSoup
from nltk.tokenize import wordpunct_tokenize
from collections import Counter
from math import log10

from pip._internal import main as pipmain


class FrequencyCounter:
    def __init__(self):
        self.pages_folder_name = join(dirname(__file__), '../task_1/pages')
        self.tokens_file_name = join(dirname(__file__), '../task_2/tokens.txt')
        self.lemmas_file_name = join(dirname(__file__), '../task_2/lemmas.txt')
        self.nlp = spacy.load("ru_core_news_sm")
        self.tokens = set()
        self.lemmas = set()
        self.read_tokens()
        self.read_lemmas()
        self.pages = []
        self.counters = []
        self.file_names = []

    def read_tokens(self):
        file = open(self.tokens_file_name, 'r')
        lines = file.readlines()
        for line in lines:
            self.tokens.add(line.strip())
        file.close()

    def read_lemmas(self):
        file = open(self.lemmas_file_name, 'r')
        lines = file.readlines()
        for line in lines:
            words = re.split('\\s+', line)
            lemma = words[0][:len(words[0]) - 1]
            self.lemmas.add(lemma)
        file.close()

    def get_tokens_data(self):
        self.pages = []
        self.counters = []
        self.file_names = []
        for file_name in listdir(self.pages_folder_name):
            file = open(self.pages_folder_name + '/' + file_name, 'r', encoding='utf-8')
            self.file_names.append(re.search('\\d+', file_name)[0])
            text = BeautifulSoup(file, features='html.parser').get_text()
            list_of_words = wordpunct_tokenize(text)
            tokens = []
            for word in list_of_words:
                if word in self.tokens:
                    tokens.append(word)
            self.pages.append(tokens)
            self.counters.append(Counter(tokens))
            file.close()

    def get_lemmas_data(self):
        self.pages = []
        self.counters = []
        self.file_names = []
        for file_name in listdir(self.pages_folder_name):
            file = open(self.pages_folder_name + '/' + file_name, 'r', encoding='utf-8')
            self.file_names.append(re.search('\\d+', file_name)[0])
            text = BeautifulSoup(file, features='html.parser').get_text()
            doc = self.nlp(text)
            lemmas = []
            for token in doc:
                lemma = token.lemma_
                if lemma in self.lemmas:
                    lemmas.append(lemma)
            self.pages.append(lemmas)
            self.counters.append(Counter(lemmas))
            file.close()

    def get_tf(self, word_in: set) -> list:
        pages_tf = []
        for page, counter in zip(self.pages, self.counters):
            count = len(page)
            tf = {}
            for word in word_in:
                tf[word] = counter[word] / count
            pages_tf.append(tf)
        return pages_tf

    def get_idf(self, count_of_pages: int, word_in: set) -> dict:
        counters = dict.fromkeys(word_in, 0)
        for p_counter in self.counters:
            for word in word_in:
                if p_counter[word] != 0:
                    counters[word] += 1
        idf = {}
        for word in word_in:
            idf[word] = log10(count_of_pages / counters[word]) if counters[word] != 0 else 0
        return idf

    def get_tf_idf(self, tf: list, idf: dict, word_in: set) -> list:
        idf_tf = []
        for tf_count in tf:
            idf_tf_dict = {}
            for word in word_in:
                idf_tf_dict[word] = tf_count[word] * idf[word]
            idf_tf.append(idf_tf_dict)
        return idf_tf

    def calculate_tf_idf_for_tokens(self):
        self.get_tokens_data()
        tf = self.get_tf(self.tokens)
        idf = self.get_idf(len(self.pages), self.tokens)
        tf_idf = self.get_tf_idf(tf, idf, self.tokens)
        for page_tf_idf, file_name in zip(tf_idf, self.file_names):
            with open(path.dirname(__file__) + f'/tokens_tf_idf/{file_name}.txt', 'w', encoding='utf-8') as file:
                for word in self.tokens:
                    file.write(f'{word} {idf[word]} {page_tf_idf[word]}\n')

    def calculate_tf_idf_for_lemmas(self):
        self.get_lemmas_data()
        tf = self.get_tf(self.lemmas)
        idf = self.get_idf(len(self.pages), self.lemmas)
        tf_idf = self.get_tf_idf(tf, idf, self.lemmas)
        for page_tf_idf, file_name in zip(tf_idf, self.file_names):
            with open(path.dirname(__file__) + f'/lemmas_tf_idf/{file_name}.txt', 'w', encoding='utf-8') as file:
                for word in self.lemmas:
                    file.write(f'{word} {idf[word]} {page_tf_idf[word]}\n')


def install_whl(path):
    pipmain(['install', path])


# install_whl('C:\\Rodion\\University\\infoSearch\\infoSearchLessons\\ru_core_news_sm-3.7.0-py3-none-any.whl')

frequencyCounter = FrequencyCounter()
frequencyCounter.calculate_tf_idf_for_tokens()
frequencyCounter.calculate_tf_idf_for_lemmas()
