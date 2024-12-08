import unittest
from ollama import chat, Client, ResponseError
from tests.test_prompts import TestPrompts
from configuration import *


class LLMTests(unittest.TestCase):

    def test_ollama(self):
        is_success = False
        try:
            client = Client(
                host=OLLAMA_HOST
            )

            stream = client.chat(model=OLLAMA_VERSION, messages=[
                {
                    'role': 'user',
                    'content': TestPrompts.TELL_ME_A_JOKE_PROMPT
                }
            ], stream=True)

            for chunk in stream:
                print(chunk['message']['content'], end='', flush=True)

            is_success = True
        except ResponseError as e:
            print(f'Error code {e.status_code}: {e.error}')

        self.assertTrue(is_success)


if __name__ == '__main__':
    unittest.main()
