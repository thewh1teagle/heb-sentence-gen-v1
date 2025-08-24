import os
import dotenv

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-5"

PROMPT = """
Generate exactly 10 Hebrew sentences. Follow these rules with no exceptions:

1. Sentence length: Each sentence must contain between 6 and 20 words (inclusive).
2. Alphabet restriction: Use only standard Hebrew letters (Unicode range U+05D0–U+05EA). No niqqud, vowels, diacritics, cantillation marks, or non-Hebrew letters.
3. Punctuation restriction: Allowed punctuation marks are limited to: period (.), comma (,), question mark (?), exclamation mark (!). Do not use any other punctuation symbols.
4. Prohibited content:
   - Do not include numbers (in any script).
   - Do not include emojis or special characters.
   - Do not include English or non-Hebrew words.
5. Style requirements:
   - Sentences should be natural, modern, and everyday Hebrew.
   - Include a mix of sentence types: statements, questions, and exclamations.
   - Keep vocabulary simple, like spoken conversation, not poetic or archaic.
6. Formatting output:
   - Write exactly one sentence per line.
   - Do not number the sentences.
   - Do not include quotes, explanations, or translations.
   - Output only the Hebrew sentences.
""".strip()