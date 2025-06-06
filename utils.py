import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import random

load_dotenv()


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_RANGE = "Sheet1!A1"
SHEET_DATA_RANGE = "Sheet1!A1:G1"  # Adjust the range as needed


def credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
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
    # Ensure 'Pending' is always set as the status if not already present
    if len(values) < 7:
        values.append("Pending")
    result = append_values(SPREADSHEET_ID, SHEET_RANGE, "RAW", values)
    if isinstance(result, HttpError):
        return None
    return result



def get_data_from_sheet():
    creds = credentials()
    try:
        service = build("sheets", "v4", credentials=creds)

        service = build("sheets", "v4", credentials=creds)
        sheet_metadata = (
            service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        )
        sheet_name = sheet_metadata["sheets"][0]["properties"]["title"]
        # Find the next empty row
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A:A")
            .execute()
        )
        num_rows = len(result.get("values", [])) + 1
        # Skip the first row (header), get all remaining rows
        range_names = [f"{sheet_name}!A2:G{num_rows}"]
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


def generate_save_test_data():
    test_data = []
    # Approximate coordinates for Yonsei University, Seoul: [37.5665, 126.9386]
    for i in range(20):
        lat = round(random.uniform(37.560, 37.570), 6)
        lng = round(random.uniform(126.930, 126.945), 6)
        row = [
            f"Author{random.randint(1, 5)}",
            f"Problem Title {i+1}",
            f"Description for problem {i+1}",
            f"2025-06-0{random.randint(1, 5)}",
            f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}",
            f"[{lat}, {lng}]",
            f"{random.choice(['Pending', 'In Progress', 'Resolved', 'Closed'])}",
        ]
        test_data.append(row)

    for row in test_data:
        save_to_sheet(row)


def update_status_in_sheet(selectors, new_status):
    """
    selectors: list of tuples (problem_title, date, time) to uniquely identify rows
    new_status: string, the new status to set
    """
    creds = credentials()
    try:
        service = build("sheets", "v4", credentials=creds)
        # Get all data
        all_data = get_data_from_sheet()
        updated = 0
        if all_data is not None:
            for idx, row in enumerate(all_data):
                if len(row) >= 7:
                    title, date, time = row[1], row[3], row[4]
                    if (title, date, time) in selectors:
                        all_data[idx][6] = new_status
                        updated += 1
        # Write back all data (excluding header)
        if updated > 0 and all_data is not None:
            body = {"values": all_data}
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"Sheet1!A2:G{len(all_data)+1}",
                valueInputOption="RAW",
                body=body,
            ).execute()
        return updated
    except HttpError:
        return 0


if __name__ == "__main__":
    generate_save_test_data()
