from contextlib import asynccontextmanager
import os
import pandas as pd
from fastapi import FastAPI
import asyncio
import json

app = FastAPI()

STOCK_EXCEL_DIR = "./stock-excel"
STOCK_JSON_DIR = "./stock-json"
STOCK_EXCEL_RESULT_DIR = "./stock-excel-result"

# Ensure JSON output directory exists
os.makedirs(STOCK_JSON_DIR, exist_ok=True)
os.makedirs(STOCK_EXCEL_DIR, exist_ok=True)
os.makedirs(STOCK_EXCEL_RESULT_DIR, exist_ok=True)

async def convert_stock_excels_to_json():
    print('Checking for excel files')
    while True:
        files = [f for f in os.listdir(STOCK_EXCEL_DIR) if f.endswith(('.xls', '.xlsx'))]
        
        for file in files:
            print('found file {file}')
            file_path = os.path.join(STOCK_EXCEL_DIR, file)
            json_file_path = os.path.join(STOCK_JSON_DIR, f"{os.path.splitext(file)[0]}.json")
            
            try:
                df = pd.read_excel(file_path)
                df.to_json(json_file_path, orient="records", indent=4)
                os.remove(file_path)  # Delete the original Excel file after conversion
                print(f"Converted {file} to JSON.")
            except Exception as e:
                print(f"Error processing {file}: {e}")
        
        await asyncio.sleep(5)  # Wait for 5 minutes before checking again

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(convert_stock_excels_to_json())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/stock-json")
async def get_stock_json():
    files = sorted([f for f in os.listdir(STOCK_JSON_DIR) if f.endswith(".json")])
    if not files:
        return {"error": "No JSON files available."}
    
    first_file = files[0]
    file_path = os.path.join(STOCK_JSON_DIR, first_file)
    
    with open(file_path, "r") as f:
        content = json.load(f)

    return {"id": first_file, "content": content}

@app.post("/stock-excel-results")
async def save_stock_json_result(payload: dict):
    file_id = payload.get("id")
    content = payload.get("content")
    
    if not file_id or not content:
        return {"error": "Invalid payload."}
    
    result_xlsx_path = os.path.join(STOCK_EXCEL_RESULT_DIR, f"{file_id}.xlsx")
    
    # Convert JSON content to DataFrame and save as XLSX
    df = pd.DataFrame(content)
    df.to_excel(result_xlsx_path, index=False)
    
    # Remove the original JSON file
    original_file_path = os.path.join(STOCK_JSON_DIR, file_id)
    if os.path.exists(original_file_path):
        os.remove(original_file_path)
    
    return {"message": "Stock result saved successfully as XLSX."}
