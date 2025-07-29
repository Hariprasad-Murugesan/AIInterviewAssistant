import requests
import json
from keys import QWEN_API_KEY
from prompts import create_prompt, INITIAL_RESPONSE
import time

# Configure Qwen3 API
API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {QWEN_API_KEY}",
    "Content-Type": "application/json"
}

# Generate response based on transcript
def generate_response_from_transcript(transcript):
    try:
        prompt = create_prompt(transcript)
        payload = {
            "model": "qwen/qwen3-0.6b-04-28:free",  # Update based on OpenRouter's model list
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "max_tokens": 500,
            "temperature": 0.7  # Optional: add for stability
        }
        
        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload), stream=True)
        response.raise_for_status()

        full_response = ""
        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8')
                if chunk_str.startswith("data: "):
                    chunk_data = chunk_str[6:]  # Remove "data: " prefix
                    if chunk_data == "[DONE]":
                        break
                    try:
                        data = json.loads(chunk_data)  # Use json.loads instead of eval for safety
                        if 'choices' in data and data['choices']:
                            delta = data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            full_response += content
                    except json.JSONDecodeError:
                        continue

        return full_response.strip()
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e}")
        if e.response is not None:
            print(f"Response body: {e.response.text}")
        return ''
    except Exception as e:
        print(f"API error: {e}")
        return ''

class QwenResponder:
    def __init__(self):
        self.response = INITIAL_RESPONSE
        self.response_interval = 2

    # Respond to transcriber, get new transcript and generate response
    def respond_to_transcriber(self, transcriber):
        while True:
            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear()
                transcript_string = transcriber.get_transcript()
                response = generate_response_from_transcript(transcript_string)

                end_time = time.time()
                execution_time = end_time - start_time

                if response != '':
                    self.response = response

                remaining_time = self.response_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(0.3)

    # Update response time interval
    def update_response_interval(self, interval):
        self.response_interval = interval