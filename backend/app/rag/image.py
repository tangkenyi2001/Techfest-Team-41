from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import os
import shutil
import tempfile
from openai import OpenAI
from typing import Dict, Any

from fastapi import APIRouter
import requests
import json

client = OpenAI()
router = APIRouter(tags=["Image"])

@router.post("/image")
async def analyze_image(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        params = {
        'models': 'genai',
        'api_user': 'key',
        'api_secret': 'secret'
    }

        # Prepare the file dictionary
        files = {'media': (file.filename, file.file, file.content_type)}
        print(f"Filename: {file.filename}, Content-Type: {file.content_type}")
        # Make the request
        r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)

        print(r)
        print(r.text)  # 
        output = json.loads(r.text)
        return  output
        # Create a temporary file
        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        #     # Copy uploaded file to the temporary file
        #     shutil.copyfileobj(file.file, temp_file)
        #     temp_file_path = temp_file.name
        
        # # Encode the image to base64
        # with open(temp_file_path, "rb") as image_file:
        #     base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        # # Call OpenAI API
        # response = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": [
        #                 {
        #                     "type": "text",
        #                     "text": "You are an expert Describe the image, and try to identify if it is photoshopped or edited,lastly, give me a verdict, REAL/FAKE/CANNOT BE DETERMINED",
        #                 },
        #                 {
        #                     "type": "image_url",
        #                     "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
        #                 },
        #             ],
        #         }
        #     ],
        # )
        
        # # Clean up
        # os.unlink(temp_file_path)
        
        # # Return the analysis
        # return {"analysis": response.choices[0].message.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
