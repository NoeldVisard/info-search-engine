import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse


class Crawler:
    def __init__(self):
        self.base_url = 'https://habr.com'
        self.request_urls = [
            'https://habr.com/ru/flows/develop/articles/',
            'https://habr.com/ru/flows/admin/articles/',
            'https://habr.com/ru/flows/design/articles/',
            'https://habr.com/ru/flows/management/articles/',
            'https://habr.com/ru/flows/marketing/articles/',
            'https://habr.com/ru/flows/popsci/articles/'
        ]
        self.class_attribute = 'tm-title__link'
        self.pages_folder_name = os.path.dirname(__file__) + '/pages'
        self.index_file_name = os.path.dirname(__file__) + '/index.txt'
        self.session = requests.Session()

        if not os.path.exists(self.pages_folder_name):
            os.mkdir(self.pages_folder_name)

    def find_pages(self):
        all_links = []
        for request_url in self.request_urls:
            page = urllib.request.urlopen(request_url)
            soup = BeautifulSoup(page, 'html.parser')
            links = []
            for link in soup.findAll('a', {'class': self.class_attribute}, href=True):
                if link.get('href')[0] == '/':
                    link = urllib.parse.urljoin(self.base_url, link.get('href'))
                    links.append(link)
            all_links.extend(links)

        return all_links

    def get_text_from_page(self, url):
        request = self.session.get(url)
        request.encoding = request.apparent_encoding
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, 'html.parser')
            bad_tags = ['style', 'link', 'script']
            for tag in soup.find_all(bad_tags):
                tag.extract()
            return str(soup)
        return None

    def download_pages(self, count: int = 100):
        all_links = list(self.find_pages())
        index_file = open(self.index_file_name, 'w', encoding='utf-8')
        file_counter = 1
        for link in all_links:
            if file_counter <= count:
                text = self.get_text_from_page(link)
                if text is None:
                    continue
                else:
                    page_name = f'{self.pages_folder_name}/page_{file_counter}.html'
                    with open(page_name, 'w', encoding='utf-8') as page:
                        page.write(text)
                    index_file.write(f'{file_counter} {link}\n')
                    file_counter += 1
            else:
                break
        index_file.close()


if __name__ == '__main__':
    crawler = Crawler()
    crawler.download_pages()