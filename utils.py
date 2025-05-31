import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_RANGE = "Sheet1!A1"
SHEET_DATA_RANGE = "Sheet1!A1:F1"  # Adjust the range as needed

def credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def append_values(spreadsheet_id, range_name, value_input_option, _values):
  creds = credentials()
  try:
    service = build("sheets", "v4", credentials=creds)
    values = [
        [
            # Cell values ...
        ],
        # Additional rows ...
    ]
    if _values:
      values = [_values]
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body,
        )
        .execute()
    )
    # print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
    return result

  except HttpError as error:
    # print(f"An error occurred: {error}")
    return error

def save_to_sheet(values):
    result = append_values(
        SPREADSHEET_ID,
        SHEET_RANGE,
        "RAW",
        values
    )
    if isinstance(result, HttpError):
        # print(f"An error occurred: {result}")
        return None
    return result

def get_data_from_sheet():
    creds = credentials()
    try:
        service = build("sheets", "v4", credentials=creds)
        
        service = build("sheets", "v4", credentials=creds)
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_name = sheet_metadata['sheets'][0]['properties']['title']
        # Find the next empty row
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="Sheet1!A:A"
        ).execute()
        num_rows = len(result.get("values", [])) + 1
        # Skip the first row (header), get all remaining rows
        range_names = [f"{sheet_name}!A2:F{num_rows}"]
        result = (
            service.spreadsheets()
            .values()
            .batchGet(spreadsheetId=SPREADSHEET_ID, ranges=range_names)
            .execute()
        )

        return result.get("valueRanges", [])[0].get("values", [])
    except HttpError:
        return None
    
def shorten_coords(coord_str):
            try:
                lat, lng = [float(x) for x in coord_str.strip("[]").split(",")]
                return f"[{lat:.3f}, {lng:.3f}]"
            except Exception:
                return coord_str
    


if __name__ == "__main__":
    data = get_data_from_sheet()
    if data:
        print("Data retrieved successfully:", data)
    else:
        print("Failed to retrieve data.")