import unittest
from ollama import chat, Client
from tests.test_prompts import TestPrompts


class LLMTests(unittest.TestCase):

    def test_ollama(self):
        client = Client(
            host='http://localhost:11434',
            headers={'x-some-header': 'some-value'}
        )

        stream = client.chat(model='llama3.1:8b', messages=[
            {
                'role': 'user',
                'content': TestPrompts.SOLVE_EQUATION_PROMPT
            }
        ], stream=True)

        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)

        self.assertIsNotNone(chunk)


if __name__ == '__main__':
    unittest.main()
