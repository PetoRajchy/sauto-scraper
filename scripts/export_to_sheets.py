import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Load scraped JSON
with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Google Sheets authentication
creds_info = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS"])
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
gc = gspread.authorize(creds)

# Open sheet and worksheets
sheet = gc.open_by_key(os.environ["SPREADSHEET_ID"])
ws_current = sheet.worksheet("CurrentData")
ws_history = sheet.worksheet("HistoryData")

# Clear CurrentData before each scrape
ws_current.clear()

# Headers including seller info
headers = [
    "id", "brand", "model", "name", "price", "year",
    "tachometer", "region", "district", "municipality",
    "url", "seller_id", "seller_name",
    "created_at", "scraped_at"
]
ws_current.append_row(headers)

# Timestamp
scraped_at = datetime.utcnow().isoformat()

# Load existing history IDs (dedupe base)
history_values = ws_history.col_values(1)
existing_history_ids = set(v.strip() for v in history_values[1:])

# Prepare rows
current_rows = []
new_history_rows = []

for item in data:
    car_id = str(item.get("id")).strip()
    row = [
        car_id,
        item.get("manufacturer_cb", {}).get("name"),
        item.get("model_cb", {}).get("name"),
        item.get("name"),
        item.get("price"),
        item.get("manufacturing_date", "")[:4],
        item.get("tachometer"),
        item.get("locality", {}).get("region"),
        item.get("locality", {}).get("district"),
        item.get("locality", {}).get("municipality"),
        f"https://www.sauto.cz/osobni/detail/{item.get('manufacturer_cb', {}).get('seo_name')}/{item.get('model_cb', {}).get('seo_name')}/{car_id}",
        str(item.get("user", {}).get("id", "") if item.get("user") else ""),
        item.get("premise", {}).get("name", "") if item.get("premise") else "",
        item.get("create_date"),
        scraped_at
    ]

    current_rows.append(row)

    if car_id not in existing_history_ids:
        new_history_rows.append(row)

# Update CurrentData
ws_current.append_rows(current_rows)

# Add only new rows to history
if new_history_rows:
    ws_history.append_rows(new_history_rows)
