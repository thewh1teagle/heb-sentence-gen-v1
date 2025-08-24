import json
import random
from pathlib import Path

PROMPT = """
Generate exactly {count} Hebrew sentences. Follow these rules with no exceptions:

1. Alphabet & punctuation
- Only Hebrew letters (U+05D0–U+05EA), spaces, and [. , ? !].
- No digits, Latin, niqqud, emojis, or other symbols.

2. Sentence length distribution
- Short (5–8 words) ≈ 25%.
- Medium (9–14 words) ≈ 35%.
- Long (15–22 words) ≈ 40%.
- Sentences must not all start similarly — vary rhythm, use adverbs, conjunctions, or prepositions at times.

3. Style diversity
- Everyday spoken Hebrew (≈ 30–35%).
- Formal/professional Hebrew (≈ 20–25%).
- Expressive/emotional Hebrew (≈ 20–25%).
- Poetic, sensory, or metaphorical (≈ 10–15%).
- At least 5 sentences must use unusual or playful phrasing.

4. Thematic range (must all appear, mix freely)
- Home & family
- School & learning
- Work & technology
- Travel & transport
- Culture & arts
- Nature & outdoors
- Food & cooking
- Social life & relationships
- Extra: health, city vs. village, community, hobbies

5. Emotional variety
Include joy, surprise, anger, calm, doubt, excitement, nostalgia, frustration.

6. Syntax variety
- Use declarative, interrogative, exclamatory, imperative.
- Vary word order: Subject–Verb–Object, Verb–Subject, Object–Verb.
- Use clauses with ש, כאשר, אם, למרות ש, כדי, בזמן ש.
- Begin some sentences with adverbs (פתאום, תמיד, לעיתים), conjunctions (אבל, כי, למרות ש), or prepositions (מתחת ל, מעל ל).

7. Narrative flow
- Organize the sentences into mini-stories of 4–6 sentences each (paragraphs).
- Each paragraph must feel like a small coherent scene, where sentences follow each other naturally.
- Still, every sentence must also make sense alone.
- Separate paragraphs with a blank line.

8. Sensory detail
- Sprinkle references to smell, taste, sound, touch, sight.
- At least 20% of sentences should include sensory description.

9. Anti-repetition
- Do not repeat openings, verbs, or common phrases too often.
- Proper names: each can appear max twice.

10. Formatting
- Exactly one sentence per line.
- Group sentences into paragraphs of 4–6 lines (mini-stories).
- Separate paragraphs with a blank line.
- No numbering, no explanations, no metadata.
- Output only the Hebrew sentences.


---

TOPIC: {topic}

examples:
{examples}
""".strip()


class Prompt:
    def __init__(self):
        root_path = Path(__file__).parent
        topics_path = root_path / "topics.json"
        with open(topics_path, "r") as f:
            self.topics: list[dict] = json.load(f)
    
    def get_prompt(self, count: int) -> str:
        random_topic = random.choice(self.topics)
        topic_name = random_topic["topic"]
        topic_examples = random_topic["examples"]
        return PROMPT.format(topic=topic_name, examples='\n'.join(topic_examples), count=count)
        


if __name__ == "__main__":
    root_path = Path(__file__).parent
    prompt = Prompt(root_path / "topics.json")
    print(prompt.get_prompt())