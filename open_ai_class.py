import openai
import time

class OpenAI_Analysis:
    def __init__(self):
        self.api_key = "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"
        self.model_engine = "text-davinci-002" #Replace with the OpenAI model engine you want to use

    def analyze_text(self, text, context, parameters):
        # Authenticate with OpenAI API
        openai.api_key = self.api_key

        # Prepare the prompt
        prompt = f"{text}\nContext: {context}\n - {parameters}\n"

        # Call OpenAI API to generate the answers
        try:
            completions = openai.Completion.create(
                engine=self.model_engine,
                prompt=prompt,
                max_tokens=40,
                n=1,
                stop=None,
                temperature=0.9,
            )

            # Parse the answers from the API response
            answers = []
            for choice in completions.choices:
                answer = choice.text.strip()
                if answer:
                    answers.append([answer])

        except openai.error.RateLimitError as e:
            print("Rate limit reached. Waiting for 1 minute before retrying...")
            time.sleep(60)
            self.analyze_text(text, context, parameters)

        return answers