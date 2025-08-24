import os
import dotenv
import argparse

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-5-mini"


parser = argparse.ArgumentParser()
parser.add_argument("output_file", type=str, help="The output file to write the generated text to")
parser.add_argument("--count", type=int, default=100, help="The number of sentences to generate")
args = parser.parse_args()