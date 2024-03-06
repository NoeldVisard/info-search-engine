import re
from pymystem3 import Mystem
from os import path


class SearchQuery:
    def __init__(self, query: str, files: set):
        self.query = query
        self.files = files

    def __and__(self, other):
        return SearchQuery(f'({self.query} & {other.query})', self.files & other.files)

    def __or__(self, other):
        return SearchQuery(f'({self.query} | {other.query})', self.files | other.files)

    def __sub__(self, other):
        return SearchQuery(f'({self.query} ! {other.query})', self.files - other.files)


class BooleanSearch:
    def __init__(self):
        self.inverted_index_file_name = path.dirname(__file__) + '/inverted_index_temp21.txt'
        self.mystem = Mystem()
        self.index = dict()
        self.read_inverted_index()

    def read_inverted_index(self):
        file = open(self.inverted_index_file_name, 'r')
        lines = file.readlines()
        for line in lines:
            items = re.split('\\s+', line)
            token = items[0]
            files = set()
            for i in range(2, len(items) - 1):
                files.add(int(items[i]))
            self.index[token] = SearchQuery(token, files)
        file.close()

    def evaluate_query(self, query_tokens):
        stack = []
        i = 0
        while i < len(query_tokens):
            if query_tokens[i] == '(':
                stack.append(query_tokens[i])
            elif query_tokens[i] == ')':
                finish = False
                while stack and stack[-1] != '(' and not finish:
                    stack.append(self.process_operator(stack.pop(), stack.pop(), stack.pop() if stack else None))
                    finish = True
                if stack:
                    lastAppended = stack.pop()
                    stack.pop()
                    stack.append(lastAppended)
            elif query_tokens[i] in {'&', '|', '!'}:
                stack.append(query_tokens[i])
            else:
                parsed_token = self.mystem.analyze(query_tokens[i])[0]
                current_token = parsed_token['analysis'][0]['lex'].lower() if 'analysis' in parsed_token else \
                    query_tokens[i].lower()
                stack.append(self.index[current_token])

            i += 1

        while len(stack) > 1:
            stack.append(self.process_operator(stack.pop(), stack.pop(), stack.pop() if stack else None))

        return stack[0]

    def process_operator(self, operand1, operator, operand2):
        if operand2 is None:
            return operand1
        elif operator == '&':
            return operand1 & operand2
        elif operator == '|':
            return operand1 | operand2
        elif operator == '!':
            return operand1 - operand2

    def search(self, search_words):
        search_words = re.findall(r'\(|\)|&|\||!|\b\w+\b', search_words)
        result = self.evaluate_query(search_words)
        if result:
            result = list(result.files)
            result.sort()
            return result
        else:
            return []


if __name__ == '__main__':
    boolean_search = BooleanSearch()

    # query = "(последнего & варианта) | (продукт & будет) | выше"
    # query = "выше"
    # query = "последнего & варианта"
    # query = "(последнего & варианта) | выше"
    query = "(последнего & варианта) | выше | работу"

    result = boolean_search.search(query)
    print(f"Result of the boolean search '{query}': {result}")
