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


def append_values(spreadsheet_id, range_name, value_input_option, _values):
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  # pylint: disable=maybe-no-member
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