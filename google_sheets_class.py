import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

sheet_id = '1pgU2eV8BiMCpdCRwub2yXvQchKDQRYSQ3IYNYVUajYQ'
worksheet = 'datacallstopareto'

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

    def write_data(self, start_row, start_col, data):
        worksheet = self.gc.open_by_key(self.sheet_id).worksheet(self.worksheet_name)

        # Write the data
        num_rows = len(data)
        num_cols = len(data[0])

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


# # Example usage
# sheet_id = '1pgU2eV8BiMCpdCRwub2yXvQchKDQRYSQ3IYNYVUajYQ'
# worksheet_name = 'datacallstopareto'
#
# # Read data from Google Sheet
# gsheet = GoogleSheet(sheet_id, worksheet_name)
# range_name = 'A1:C2'
# data = gsheet.get_data(range_name)
# print(data)
#
# # Write data to Google Sheet
# start_row = 1
# start_col = 12
# data = [['John', 25, 'Male'], ['Jane', 30, 'Female'], ['Bob', 45, 'Male']]
# gsheet.write_data(start_row, start_col, data)
