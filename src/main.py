from config import MODEL, OPENAI_API_KEY, args
from prompt import Prompt
import openai
from tqdm import tqdm

def main():
    
    output_file: str = args.output_file
    count: int = args.count

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    for _ in tqdm(range(count)):
        prompt = Prompt()
        prompt_text = prompt.get_prompt(10)
        response = client.responses.create(
            model=MODEL,
            input=[
                {
                "role": "user",
                "content": [
                    {
                    "type": "input_text",
                    "text": prompt_text
                    }
                ]
                }
            ],
            text={
                "format": {
                "type": "text"
                },
                "verbosity": "medium"
            },
            reasoning={
                "effort": "minimal"
            },
            tools=[],
        )
        text = response.output_text
        text = '\n'.join(i.strip() for i in text.splitlines() if i.strip())
        
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(text + '\n')

if __name__ == "__main__":
    main()