import re

class Lexer:
    # Define token types
    TOKENS = [
        ('STRING', r'"([^\\"]|\\.)*"'),  # Match strings
        ('NUMBER', r'\d+'),               # Match integers
        ('PLUS', r'\+'),                  # Match plus operator
        ('MINUS', r'-'),                  # Match minus operator
        ('TIMES', r'\*'),                 # Match multiplication operator
        ('DIVIDE', r'/'),                 # Match division operator
        ('LPAREN', r'\('),                # Match left parenthesis
        ('RPAREN', r'\)'),                # Match right parenthesis
        ('WHITESPACE', r'\s+'),           # Match whitespace (to ignore)
    ]

    def __init__(self, text):
        self.text = text
        self.position = 0
        self.tokens = self.tokenize()

    def tokenize(self):
        token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKENS)
        token_regex = re.compile(token_regex)

        tokens = []
        for match in token_regex.finditer(self.text):
            kind = match.lastgroup
            value = match.group(kind)

            if kind == 'WHITESPACE':
                continue  # Ignore whitespace
            elif kind == 'STRING':
                tokens.append((kind, value[1:-1]))  # Strip quotes
            else:
                tokens.append((kind, value))
        
        return tokens

    def next_token(self):
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        return None

    def peek(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def error(self):
        raise Exception("Syntax error")

    def eat(self, token_type):
        if self.current_token and self.current_token[0] == token_type:
            self.current_token = self.lexer.next_token()
        else:
            self.error()

    def parse(self):
        return self.expression()

    def expression(self):
        result = self.term()

        while self.current_token and self.current_token[0] in ('PLUS', 'MINUS'):
            token = self.current_token
            if token[0] == 'PLUS':
                self.eat('PLUS')
                result += self.term()
            elif token[0] == 'MINUS':
                self.eat('MINUS')
                result -= self.term()
        
        return result

    def term(self):
        result = self.factor()

        while self.current_token and self.current_token[0] in ('TIMES', 'DIVIDE'):
            token = self.current_token
            if token[0] == 'TIMES':
                self.eat('TIMES')
                result *= self.factor()
            elif token[0] == 'DIVIDE':
                self.eat('DIVIDE')
                result /= self.factor()
        
        return result

    def factor(self):
        token = self.current_token

        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return int(token[1])
        elif token[0] == 'STRING':
            self.eat('STRING')
            return token[1]  # Return string without quotes
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            result = self.expression()
            self.eat('RPAREN')
            return result

        self.error()

def evaluate(input_string):
    lexer = Lexer(input_string)
    parser = Parser(lexer)
    result = parser.parse()
    return result

# Example usage
if __name__ == '__main__':
    while True:
        try:
            s = input('custom_language > ')
            if s == 'exit':
                break
            result = evaluate(s)
            print(result)
        except Exception as e:
            print(e)
