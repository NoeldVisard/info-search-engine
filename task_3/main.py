import re
from os import listdir, path
from os.path import dirname, join
from bs4 import BeautifulSoup
from nltk.tokenize import wordpunct_tokenize
from pip._internal import main as pipmain
import spacy


class IndexEntry:
    def __init__(self):
        self.count = 0
        self.files = set()

    def update(self, count, file_number):
        self.count += count
        self.files.add(int(file_number))


class InvertedIndex:
    def __init__(self):
        self.pages_folder_name = join(dirname(__file__), '../task_1/pages')
        self.lemmas_file_name = join(dirname(__file__), '../task_2/lemmas.txt')
        self.inverted_index_file_name = path.join(dirname(__file__), 'inverted_index_kchau.txt')
        self.spacy = spacy.load("ru_core_news_sm")
        self.lemmas = dict()
        self.index = dict()

    def read_list_of_lemmas(self):
        with open(self.lemmas_file_name, 'r') as file:
            lines = file.readlines()
            for line in lines:
                words = re.split('\\s+', line)
                key = words[0][:len(words[0]) - 1]
                self.lemmas[key] = set(words[1:-1])

    def get_index(self):
        for i, file_name in enumerate(listdir(self.pages_folder_name)):
            with open(join(self.pages_folder_name, file_name), 'r', encoding='utf-8') as file:
                text = BeautifulSoup(file, features='html.parser').get_text()
                list_of_words = wordpunct_tokenize(text)

                for word in list_of_words:
                    analysis = self.spacy(word)
                    lemma = analysis[0].lemma_

                    if lemma in self.lemmas and lemma not in self.index:
                        count = sum(list_of_words.count(wf) for wf in self.lemmas[lemma])
                        self.index[lemma] = IndexEntry()
                        self.index[lemma].update(count, re.search('\\d+', file_name)[0])
                    elif lemma in self.lemmas:
                        self.index[lemma].update(1, re.search('\\d+', file_name)[0])

    def write_index(self):
        with open(self.inverted_index_file_name, 'w') as file:
            for word, entry in self.index.items():
                line = f"{word} ({entry.count}): {' '.join(map(str, sorted(entry.files)))}\n"
                file.write(line)

    def create_index_file(self):
        self.read_list_of_lemmas()
        self.get_index()
        self.write_index()


def install_whl(path):
    pipmain(['install', path])


inverted_index = InvertedIndex()
inverted_index.create_index_file()

# install_whl('C:\\Users\\digital\\Downloads\\ru_core_news_sm-3.7.0-py3-none-any.whl')
