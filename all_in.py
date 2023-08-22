import base64
import hashlib
import io
import json
import os
import time
import requests

from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from google.cloud import bigquery
from google.cloud import language_v1
from google.cloud.language_v1.types import Document, EncodingType
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import gspread
import openai

# For GoogleSpeechToText, you will also need to install the following package:
# pip install google-cloud-speech
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1.types import RecognitionConfig, RecognitionAudio

class GoogleSheet:
    def __init__(self, sheet_id, worksheet_name):
        self.sheet_id = sheet_id
        self.worksheet_name = worksheet_name
        self.gc = self.get_google_sheets_api()

    def get_google_sheets_api(self):
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name('openai-infotelligent-5a47db1ca5dd.json', scope)
        return gspread.authorize(creds)

    def get_data_cols(self, range_name):
        worksheet = self.gc.open_by_key(self.sheet_id).worksheet(self.worksheet_name)
        data = worksheet.range(range_name)

        # Convert data to a list of lists
        rows = []
        current_row = []
        for cell in data:
            current_row.append(cell.value)
            if cell.col == data[-1].col:
                rows.append(current_row)
                current_row = []

        return rows

    def get_data_rows(self, range_name):
        worksheet = self.gc.open_by_key(self.sheet_id).worksheet(self.worksheet_name)
        data = worksheet.range(range_name)

        # Convert data to a list of columns
        cols = [[] for i in range(data[-1].col)]
        current_col = 0
        for cell in data:
            cols[current_col].append(cell.value)
            if cell.col == data[-1].col:
                current_col = 0
            else:
                current_col += 1

        return cols

    def write_data(self, start_row, start_col, data, check_starting_cell=False):
        worksheet = self.gc.open_by_key(self.sheet_id).worksheet(self.worksheet_name)

        # Write the data
        num_rows = len(data)
        num_cols = len(data[0])

        if check_starting_cell:
            # Check if the starting cell is blank
            starting_cell = worksheet.cell(start_row, start_col)
            if starting_cell.value != '':
                cell_range = worksheet.range(start_row + 1, start_col, worksheet.row_count, start_col)
                empty_cells = [cell for cell in cell_range if cell.value == '']
                if len(empty_cells) > 0:
                    start_row = empty_cells[0].row
                else:
                    start_row = worksheet.row_count + 1

        end_row = start_row + num_rows - 1
        end_col = start_col + num_cols - 1

        range_str = f"{chr(start_col + 96)}{start_row}:{chr(end_col + 96)}{end_row}"
        cell_list = worksheet.range(range_str)

        for i, cell in enumerate(cell_list):
            cell.value = data[i // num_cols][i % num_cols]
        worksheet.update_cells(cell_list)

    def get_last_row_number(self, range_name):
        worksheet = self.gc.open_by_key(self.sheet_id).worksheet(self.worksheet_name)
        data = worksheet.range(range_name)

        # Check the last row for any non-empty cells
        last_row = len(data)
        while last_row >= 1:
            if data[last_row - 1].value != '':
                return data[last_row - 1].row
            last_row -= 1
        return 1

    def get_last_filled_column(self, row=1):
        data = self.get_data_rows(f'A{row}:Z{row}')
        last_filled_col = 0
        for i, col in enumerate(data):
            if col[0] != '':
                last_filled_col = i + 1
        return last_filled_col

    def get_column_letter_by_text(self, search_text):
        search_range = f"A1:{chr(96 + self.get_last_filled_column())}1"
        data = self.get_data_rows(search_range)
        for i, col in enumerate(data):
            if col[0] == search_text:
                return chr(97 + i)
        return None


class GoogleDriveFile:
    def __init__(self, file_link):
        self.file_link = file_link
        self.file_id = self.get_file_id()
        self.service = self.build_service()

    def get_file_id(self):
        # Extract the file ID from the Google Drive link
        file_id = None
        parts = self.file_link.split('/')
        for i in range(len(parts)):
            if parts[i] == 'd':
                file_id = parts[i+1]
                break
        return file_id

    def build_service(self):
        # Build the Google Drive API service
        scope = ['https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('openai-infotelligent-5a47db1ca5dd.json', scope)
        service = build('drive', 'v3', credentials=creds)
        return service

    def read_contents(self):
        # Download the file contents and return them as a string
        try:
            request = self.service.files().get_media(fileId=self.file_id)
            content = io.BytesIO()
            downloader = MediaIoBaseDownload(content, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()
            content.seek(0)
            return content.getvalue()
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None


class TextAnalysisAdapter:
    class OpenAI_Analysis:
        def __init__(self):
            self.api_key = "OPENAI_API_KEY"
            self.model_engine = "text-davinci-003"  # Replace with the OpenAI model engine you want to use

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
                    max_tokens=10,
                    n=1,
                    stop=None,
                    temperature=0.5,
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


    class GoogleTextAnalysis:
        def __init__(self):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/google_credentials.json"
            self.client = language_v1.LanguageServiceClient()

        def analyze_text(self, text, context, parameters):
            document = language_v1.types.Document(
                content=text,
                type=enums.Document.Type.PLAIN_TEXT
            )

            encoding_type = EncodingType.UTF8
            sentiment = self.client.analyze_sentiment(document, encoding_type=encoding_type).document_sentiment

            # You can customize the analysis using different API methods provided by Google's Natural Language API
            # such as analyze_entities, analyze_entity_sentiment, analyze_syntax, etc.
            # Reference: https://googleapis.dev/python/language/latest/language_v1/api.html

            result = {
                'sentiment_score': sentiment.score,
                'sentiment_magnitude': sentiment.magnitude
            }

            return result


class SttAdapter:
    class OpenAISpeechToText:
        def __init__(self, api_key="OPENAI_API_KEY", engine="whisper-1"):  # Add engine argument
            self.engine = engine
            self.api_key = api_key

        def transcribe_audio_content(self, audio_content, audio_extension):
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.engine,
                "audio": base64.b64encode(audio_content).decode("utf-8"),
                "content_type": f"audio/{audio_extension}"
            }
            response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers,
                                     data=json.dumps(data))

            if response.status_code == 200:
                response_json = response.json()
                if 'text' in response_json:
                    return response_json["text"]
                else:
                    print("Error: 'text' key not found in the response")
                    print("Response content:", response.content)
                    return None
            else:
                print("Error getting transcription. Response status code:", response.status_code)
                print("Response content:", response.content)
                return None


    class GoogleSpeechToText:
        def __init__(self, credential_path, language_code="en-US"):
            self.credential_path = credential_path
            self.language_code = language_code

        def transcribe_audio_content(self, content, file_format):
            from google.cloud import speech_v1p1beta1 as speech
            from google.cloud.speech_v1p1beta1.types import RecognitionConfig, RecognitionAudio

            client = speech.SpeechClient.from_service_account_file(self.credential_path)

            if file_format == "wav":
                encoding = RecognitionConfig.AudioEncoding.LINEAR16
            elif file_format == "flac":
                encoding = RecognitionConfig.AudioEncoding.FLAC
            else:
                raise ValueError("Unsupported audio format")

            # Set the recognition configuration without specifying the sample rate
            config = RecognitionConfig(
                encoding=encoding,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
            )

            audio = RecognitionAudio(content=content)

            response = client.recognize(config=config, audio=audio)

            # Concatenate all the transcriptions from the response
            transcription = ""
            for result in response.results:
                transcription += result.alternatives[0].transcript

            return transcription


def main():

    sheet_id = 'GOOGLESHEET_ID'
    worksheet_name = 'datacallstopareto'

    # Initialize the Google Sheet object
    sheet = GoogleSheet(sheet_id, worksheet_name)

    # Get the column labels to search for in the first row from the user
    stt_model = input("Choose STT model (openai or google): ").lower().strip()
    analysis_model = input("Choose text analysis model (openai or google): ").lower().strip()
    text_column_label = input("Enter the label of the column containing the texts: ")
    context_column_label = input("Enter the label of the column containing the contexts: ")
    recording_column_label = input("Enter the label of the column containing the call recording links: ")

    text_column_letter = sheet.get_column_letter_by_text(text_column_label)
    context_column_letter = sheet.get_column_letter_by_text(context_column_label)
    recording_column_letter = sheet.get_column_letter_by_text(recording_column_label)

    if not text_column_letter or not context_column_letter or not recording_column_letter:
        print("Error: Unable to find the specified columns.")
        return

    # Initialize the Text Analysis object
    if analysis_model == "openai":
        analysis = TextAnalysisAdapter.OpenAITextAnalysis()
    elif analysis_model == "google":
        analysis = TextAnalysisAdapter.GoogleTextAnalysis()
    else:
        print("Invalid text analysis model choice.")
        return

    # Read the data from the Google Sheet
    last_row = sheet.get_last_row_number(f'{text_column_letter}2:{text_column_letter}')
    texts = sheet.get_data_cols(f'{text_column_letter}2:{text_column_letter}{last_row}')
    contexts = sheet.get_data_cols(f'{context_column_letter}2:{context_column_letter}{last_row}')
    recordings = sheet.get_data_cols(f'{recording_column_letter}2:{recording_column_letter}{last_row}')

    last_filled_col = sheet.get_last_filled_column()

    # Get and write parameters
    parameters = []
    while True:
        parameter = input("Enter a parameter (leave blank to finish): ")
        if not parameter:
            break
        parameters.append(parameter)

    parameter_start_col = last_filled_col + 1
    for i, parameter in enumerate(parameters):
        sheet.write_data(1, parameter_start_col + i, [[parameter]], check_starting_cell=False)

    # Initialize the STT model
    if stt_model == "openai":
        stt = SttAdapter.OpenAISpeechToText("your-openai-api-key", "whisper-1")
    elif stt_model == "google":
        stt = SttAdapter.GoogleSpeechToText("path/to/google_credentials.json")
    else:
        print("Invalid STT model choice.")
        return

    # Analyze text and write answers
    for i, (text, context, recording) in enumerate(zip(texts, contexts, recordings)):
        if not text[0] and not context[0] and not recording[0]:
            print("Error: Text, context, and recording are all empty. Stopping the script.")
            break

        if not text[0] and recording[0]:
            audio_file = GoogleDriveFile(recording[0])
            audio_content = audio_file.read_contents()
            transcription = stt.transcribe_audio_content(audio_content, "wav")

        for j, parameter in enumerate(parameters):
            print(f"Analyzing question {i + 1}")

            row_number = i + 2
            start_col = parameter_start_col + j

            answers = analysis.analyze_text(text[0], context[0], parameter)

            for answer in answers:
                sheet.write_data(row_number, start_col, [answer])

            time.sleep(10)

if __name__ == '__main__':
    main()