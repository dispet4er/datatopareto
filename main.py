from google_sheets_class import GoogleSheet
from open_ai_class import OpenAI_Analysis
import time

sheet_id = '1pgU2eV8BiMCpdCRwub2yXvQchKDQRYSQ3IYNYVUajYQ'
worksheet_name = 'datacallstopareto'

def main():
    # Initialize the Google Sheet object
    sheet = GoogleSheet(sheet_id, worksheet_name)

    # Initialize the OpenAI Analysis object
    analysis = OpenAI_Analysis()

    # Read the data from the Google Sheet
    text_range = 'I2:I'
    context_range = 'J2:J'
    parameter_range = 'K1:Z1'
    last_row = sheet.get_last_row_number(text_range)  # Ending row of the data range (including the last row)

    texts = sheet.get_data_cols(f'{context_range}{last_row}')
    contexts = sheet.get_data_cols(f'{text_range}{last_row}')
    parameters = sheet.get_data_rows(f'{parameter_range}')

    row_number = 1  # Start writing from row 1
    param_index = 0  # Start with the first parameter
    start_col = 11  # Initialize start_col

    while param_index <= 16:
        for i, (text, context) in enumerate(zip(texts, contexts)):
            print(f"Analyzing question {i + 1}")
            answers = analysis.analyze_text(text[0], context[0], parameters[param_index])

            # Write the answers back to the Google Sheet
            for answer in answers:
                sheet.write_data(row_number, start_col, [answer])

            # Increment row number
            row_number += 1

            # Increment the parameter index and start_col if we've gone through all the texts
            if (i + 1) % len(texts) == 0:
                if param_index < len(parameters) - 1:
                    param_index += 1
                    start_col += 1
                    row_number = 1

            # Pause for 10 seconds after each write request to stay under the limit of 30 requests per minute
            time.sleep(10)


if __name__ == '__main__':
    main()
