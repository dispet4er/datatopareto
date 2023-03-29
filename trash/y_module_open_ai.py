import openai
import time
from y_db_config import DB_CONFIG

# Set up the OpenAI API client
openai.api_key = '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'

# Define the context information
context = 'this is a cold call that pursues several goals: 1 - to schedule a video call in order to show the capabilities of the platform (the platform provides access to customer contact data), 2 - if the person with whom the conversation is held is not a person who can make a decision on this issue, you need to understand who could it be. During the call, the agent must conduct a dialogue with the client, answer questions, handle objections'

# Get the calls from the calls table in the database
with DB_CONFIG.connect() as conn:
    result = conn.execute("SELECT call_text, campaign_id FROM calls")
    for row in result.fetchall():
        # Extract the call text and campaign ID from the current row
        call = row[0]
        campaign_id = row[1]

        # Get the list of categories for the current campaign from the database
        categories = []
        with DB_CONFIG.connect() as conn:
            result = conn.execute("SELECT category_name FROM categories WHERE campaign_id = ?", campaign_id)
            categories = [row[0] for row in result.fetchall()]

        # Generate responses to each question for the current call
        responses = []
        for category in categories:
            question = f'{category}?'
            prompt = f'{context}\n\nCall: {call}\n\nQuestion: {question}\nAnswer:'
            parameters = {
                'model': 'text-davinci-002',
                'prompt': prompt,
                'temperature': 0.5,
                'max_tokens': 10,
                'stop': '\n'
            }
            response = None
            while response is None:
                try:
                    response = openai.Completion.create(**parameters)
                except openai.error.RateLimitError:
                    print('Rate limit reached. Waiting 1 minute before retrying...')
                    time.sleep(60)
            answer = response.choices[0].text.strip()
            responses.append(answer)

        # Print the responses to each question for the current call
        print(f'Call: {call}')
        for i, response in enumerate(responses):
            category = categories[i]
            print(f'{category}: {response}')
        print()