import os.path
import streamlit as st
import pandas as pd
import numpy as np


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "11qkTYSB8I5yIfnCZmrCiSzCbN2y4etuI7OoeS4N_FDc"
SAMPLE_RANGE_NAME = "Sheet1!A1:A1"


st.title("연세대학교 민원 맵")
st.markdown("# Main Page")