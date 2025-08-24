"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
"""
from phonikud_onnx import Phonikud
import argparse
import re
from tqdm import tqdm

model = Phonikud('phonikud-1.0.int8.onnx')


def phonemize_stress(text: str) -> str:
    text = model.add_diacritics(text)
    text = re.sub(r'[\u0590-\u059F\u05a0-\u05aa\u05ac-\u05c7\|]', '', text)
    return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="The input file to phonemize")
    parser.add_argument("output_file", type=str, help="The output file to write the phonemized text to")
    args = parser.parse_args()
    with open(args.input_file, "r", encoding="utf-8") as f:
        text = f.read()
    output = []
    for line in tqdm(text.splitlines()):
        phonemized_text = phonemize_stress(line)
        output.append(phonemized_text)
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output))