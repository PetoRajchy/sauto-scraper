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

# Open sheet and worksheet
sheet = gc.open_by_key(os.environ["SPREADSHEET_ID"])
worksheet = sheet.worksheet("RawData")

# Clear previous content
worksheet.clear()

# Header row
headers = [
    "brand", "model", "name", "price", "year",
    "tachometer", "region", "district",
    "municipality", "url", "created_at", "scraped_at"
]
worksheet.append_row(headers)

# Timestamp for scrape
scraped_at = datetime.utcnow().isoformat()

# Process and insert rows
rows = []
for item in data:
    rows.append([
        item.get("manufacturer_cb", {}).get("name"),
        item.get("model_cb", {}).get("name"),
        item.get("name"),
        item.get("price"),
        item.get("manufacturing_date", "")[:4],
        item.get("tachometer"),
        item.get("locality", {}).get("region"),
        item.get("locality", {}).get("district"),
        item.get("locality", {}).get("municipality"),
        f"https://www.sauto.cz/osobni/detail/{item.get('manufacturer_cb', {}).get('seo_name')}/{item.get('model_cb', {}).get('seo_name')}/{item.get('id')}",
        item.get("create_date"),
        scraped_at
    ])

worksheet.append_rows(rows)
