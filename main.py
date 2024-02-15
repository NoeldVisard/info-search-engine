import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse


class Crawler:
    def __init__(self):
        self.base_url = 'https://habr.com'
        self.request_url = 'https://habr.com/ru/flows/develop/articles/'
        self.class_attribute = 'tm-title__link'
        self.pages_folder_name = os.path.dirname(__file__) + '/pages'
        self.index_file_name = os.path.dirname(__file__) + '/index.txt'
        os.mkdir(self.pages_folder_name)

    def find_pages(self):
        page = urllib.request.urlopen(self.request_url)
        soup = BeautifulSoup(page, 'html.parser')
        links = []
        for link in soup.findAll('a', {'class': self.class_attribute}, href=True):
            if link.get('href')[0] == '/':
                link = urllib.parse.urljoin(self.base_url, link.get('href'))
                links.append(link)
        return links

    def get_text_from_page(self, url):
        request = requests.get(url)
        request.encoding = request.apparent_encoding
        if request.status_code == 200:
            soup = BeautifulSoup(urllib.request.urlopen(url), 'html.parser')
            bad_tags = ['style', 'link', 'script']
            for tag in soup.find_all(bad_tags):
                tag.extract()
            return str(soup)
        return None

    def download_pages(self, count: int = 100):
        links = list(set(self.find_pages()))
        index_file = open(self.index_file_name, 'w', encoding='utf-8')
        i = 1
        for link in links:
            if i <= count:
                text = self.get_text_from_page(link)
                if text is None:
                    continue
                else:
                    page_name = self.pages_folder_name + '/выкачка_' + str(i) + '.html'
                    page = open(page_name, 'w', encoding='utf-8')
                    page.write(text)
                    page.close()
                    index_file.write(str(i) + ' ' + link + '\n')
                    i += 1
            else:
                break
        index_file.close()


if __name__ == '__main__':
    crawler = Crawler()
    crawler.download_pages()