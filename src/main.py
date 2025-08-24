import os
from pathlib import Path
from typing import Optional
from openai import OpenAI, BadRequestError, APIError
import dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")  # Default to gpt-4o, override with env var
OUTPUT_FILE = Path("hebrew_sentences.txt")
BATCH_SIZE = 10  # Reduced for debugging; increase to 100 after confirming
TOTAL_COUNT = 1000  # Total sentences to generate

def get_base_rules(count: int) -> str:
    return f"""
Generate exactly {count} Hebrew sentences. Follow these rules with no exceptions:

1. Sentence length distribution:
   - All sentences must contain between 6 and 20 words (inclusive).
   - Ensure variety in length:
     * About 30% short (6–9 words).
     * About 40% medium (10–14 words).
     * About 30% long (15–20 words).

2. Alphabet restriction:
   - Use only standard Hebrew letters (Unicode range U+05D0–U+05EA).
   - No niqqud, vowels, diacritics, cantillation marks, or non-Hebrew letters.

3. Punctuation restriction:
   - Allowed punctuation marks: period (.), comma (,), question mark (?), exclamation mark (!).
   - Do not use any other punctuation symbols.

4. Prohibited content:
   - Do not include numbers (in any script).
   - Do not include emojis or special characters.
   - Do not include English or non-Hebrew words.

5. Style and diversity requirements:
   - Sentences must sound natural, modern, and fluent Hebrew.
   - Ensure wide variety in tone, phrasing, and context.
   - Distribute sentences approximately as follows:
     * 40% everyday casual / spoken Hebrew (colloquial, natural conversations, light slang).
     * 30% formal / professional Hebrew (workplace, instructions, announcements).
     * 30% expressive Hebrew (emotions, excitement, frustration, exclamations, rhetorical questions).
   - Cover a variety of situations: home, family, school, work, technology, nature, culture, shopping, travel, social life.
   - Vary emotional tone: positive, negative, neutral, surprised, enthusiastic, doubtful.
   - Avoid repeating sentence structures.

6. Formatting output:
   - Write exactly one sentence per line.
   - Do not number the sentences.
   - Do not include quotes, explanations, or translations.
   - Output only the Hebrew sentences.
""".strip()




REQUEST_HINT = lambda count: f"Make sure there are exactly {count} lines in the output."

def build_input(try_cache: bool, count: int):
    system_content = {"type": "input_text", "text": get_base_rules(count)}
    if try_cache:
        system_content["cache_control"] = {"type": "prompt"}
    return [
        {"role": "system", "content": [system_content]},
        {"role": "user", "content": [{"type": "input_text", "text": REQUEST_HINT(count)}]},
    ]

def extract_text(resp) -> str:
    """
    Extract text from API response, handling various structures.
    """
    logger.info("Extracting text from response")
    try:
        # Log raw response for debugging
        logger.debug(f"Raw response: {resp}")

        # 1) Simple path: output_text
        text = getattr(resp, "output_text", None)
        if isinstance(text, str) and text.strip():
            logger.info("Extracted text from output_text")
            return text

        # 2) Walk output -> content
        output = getattr(resp, "output", None)
        if isinstance(output, list):
            parts = []
            for item in output:
                content = item.get("content") if isinstance(item, dict) else None
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") in ("output_text", "text", "input_text"):
                            t = c.get("text")
                            if isinstance(t, str):
                                parts.append(t)
            if parts:
                text = "\n".join(parts).strip()
                logger.info("Extracted text from output.content")
                return text

        # 3) Try choices -> message -> content
        choices = getattr(resp, "choices", None)
        if isinstance(choices, list) and choices:
            msg = getattr(choices[0], "message", None)
            if msg and getattr(msg, "content", None):
                logger.info("Extracted text from choices[0].message.content")
                return msg.content

        # 4) Last resort: str(resp)
        logger.warning("No text found in expected fields, returning empty string")
        return ""
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return ""

def request_once(client: OpenAI, try_cache: bool, count: int):
    kwargs = {
        "model": MODEL,
        "input": build_input(try_cache, count),
        "text": {"verbosity": "low"},
        "reasoning": {"effort": "low"},
        "max_output_tokens": 4000,
    }
    if try_cache:
        kwargs["extra_headers"] = {"OpenAI-Beta": "prompt-caching-1"}
    try:
        logger.info(f"Making API call with try_cache={try_cache}, count={count}")
        resp = client.responses.create(**kwargs)
        logger.info("API call successful")
        return resp
    except BadRequestError as e:
        logger.error(f"BadRequestError: {e}")
        raise
    except APIError as e:
        logger.error(f"APIError: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY is not set")
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=api_key)

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
        logger.info(f"Cleared output file: {OUTPUT_FILE}")

    total_lines = []
    batches = (TOTAL_COUNT + BATCH_SIZE - 1) // BATCH_SIZE  # Ceiling division
    for batch in range(batches):
        batch_count = min(BATCH_SIZE, TOTAL_COUNT - len(total_lines))
        logger.info(f"Generating batch {batch + 1}/{batches} ({batch_count} sentences)")
        try:
            resp = request_once(client, try_cache=True, count=batch_count)
        except BadRequestError:
            logger.info("Retrying without prompt caching")
            try:
                resp = request_once(client, try_cache=False, count=batch_count)
            except Exception as e:
                logger.error(f"Failed batch {batch + 1}: {e}")
                continue

        text = extract_text(resp)
        batch_lines = [ln for ln in text.splitlines() if ln.strip()]
        total_lines.extend(batch_lines)

        if not batch_lines:
            logger.warning(f"Batch {batch + 1} returned no sentences")
        else:
            logger.info(f"Batch {batch + 1} generated {len(batch_lines)} sentence(s)")
            with OUTPUT_FILE.open("a", encoding="utf-8") as f:
                for line in batch_lines:
                    f.write(line + "\n")
                    f.flush()  # Flush each line to disk
                    logger.debug(f"Wrote line: {line}")

    if len(total_lines) != TOTAL_COUNT:
        logger.warning(f"Expected {TOTAL_COUNT} lines, got {len(total_lines)}")
        if total_lines:
            preview_raw = "\\n".join(total_lines[:5])
            logger.info(f"Raw text preview (first 5 lines): {preview_raw}")
        else:
            logger.error("No text extracted from any batch")
    else:
        logger.info(f"Generated {TOTAL_COUNT} sentence(s) successfully")

    logger.info(f"Wrote {len(total_lines)} line(s) to {OUTPUT_FILE.resolve()}")

    if total_lines:
        print("\nPreview:")
        for ln in total_lines[: min(5, len(total_lines))]:
            print(ln)

    print("\n--- Token usage ---")
    try:
        resp = request_once(client, try_cache=True, count=1)
    except BadRequestError:
        logger.info("Retrying token usage call without prompt caching")
        resp = request_once(client, try_cache=False, count=1)

    usage = getattr(resp, "usage", None)
    if usage:
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)
        if prompt_tokens is not None:
            print(f"Input tokens:  {prompt_tokens}")
        if completion_tokens is not None:
            print(f"Output tokens: {completion_tokens}")
        if total_tokens is not None:
            print(f"Total tokens:  {total_tokens}")
        if not any([prompt_tokens, completion_tokens, total_tokens]):
            print("(no token usage details available)")
            logger.info("No token usage details available")
    else:
        print("(no token usage info returned by API)")
        logger.info("No token usage info returned by API")

if __name__ == "__main__":
    main()