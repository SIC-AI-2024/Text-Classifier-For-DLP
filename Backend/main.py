import sys
import os
import joblib
from fastapi import FastAPI, File, UploadFile, HTTPException
import logging
from src.twoStepClassifier import TwoStepClassifier
import magic
import PyPDF2
import docx
from PIL import Image
import pytesseract
import nltk
from typing import List, Optional
import numpy as np
# Set up logging
logging.basicConfig(level=logging.INFO)
import pandas as pd
logger = logging.getLogger(__name__)
MAX_FILE_SIZE = 20 * 1024 * 1024
# Initialize FastAPI app
app = FastAPI()

# Make sure the path to the models folder is included in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Define the paths for the models
MODEL_PATH = "./src/models/"
DATA_PATH = "./src/data/"
MODEL_1_PATH = os.path.join(MODEL_PATH, "model_1_noenron.pkl")
MODEL_2_PATH = os.path.join(MODEL_PATH, "model_2_noenron.pkl")
VECTORIZER_PATH = os.path.join(MODEL_PATH, "tfidf_vectorizer_noenron.pkl")
PII_FILE_PATH = os.path.join(DATA_PATH, "pii_bank_cc_private.csv")
LEGAL_FILE_PATH = os.path.join(DATA_PATH, "google_private.csv")
PROCEDURE_FILE_PATH = os.path.join(DATA_PATH, "dyncorp_private.csv")


# Load models and vectorizer at startup (to avoid loading on each request)
try:
    model_1 = joblib.load(MODEL_1_PATH)
    model_2 = joblib.load(MODEL_2_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)

    # Read data from CSV files and extract 'content' column
    pii_df = pd.read_csv(PII_FILE_PATH)
    legal_df = pd.read_csv(LEGAL_FILE_PATH)
    procedure_df = pd.read_csv(PROCEDURE_FILE_PATH)

    corpora_vector = {
        'legal': vectorizer.transform(legal_df['content'].tolist()),
        'pii': vectorizer.transform(pii_df['content'].tolist()),
        'procedure': vectorizer.transform(procedure_df['content'].tolist())
    }

    logger.info("Models and vectorizer loaded successfully.")

except FileNotFoundError:
    logger.error("One or more data files not found.")
    raise HTTPException(status_code=404, detail="Data file not found.")
except pd.errors.EmptyDataError:
    logger.error("One or more data files are empty.")
    raise HTTPException(status_code=500, detail="Data file is empty.")
except KeyError:
    logger.error("Data file is missing the 'content' column.")
    raise HTTPException(status_code=500, detail="Data file is missing the 'content' column.")
except Exception as e:
    logger.error(f"Error loading models or data: {str(e)}")
    raise HTTPException(status_code=500, detail="Failed to load models or data.")

# Initialize the two-step classifier once
two_step_classifier = TwoStepClassifier(vectorizer,model_1, model_2 , corpora_vector)

# Define your file extraction functions

def extract_text_from_pdf(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting text from DOCX: {str(e)}")

def extract_text_from_image(file_path: str) -> str:
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting text from image: {str(e)}")

def extract_text(file_path: str) -> str:
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    logger.info(f"File type detected: {file_type}")

    if "pdf" in file_type:
        return extract_text_from_pdf(file_path)
    elif "msword" in file_type or "word" in file_type:
        return extract_text_from_docx(file_path)
    elif "image" in file_type:
        return extract_text_from_image(file_path)
    else:
        raise HTTPException(status_code=415, detail="Unsupported file type")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Text Extractor! 🌟"}
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from typing import List, Optional

@app.post("/extract-text/")
async def extract_text_from_files_and_text(
    files: Optional[List[UploadFile]] = File(None),
    text: Optional[str] = Form(None)
):
    temp_file_paths = []
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')
    print("Downloaded")
    try:
        file_contents = []

        if files:
            for file in files:
                temp_file_path = f"/tmp/{file.filename}"
                temp_file_paths.append(temp_file_path)

                logger.info(f"Received file: {file.filename}")

                with open(temp_file_path, "wb") as f:
                    f.write(await file.read())

                logger.info(f"File saved to {temp_file_path}")

                extracted_text = extract_text(temp_file_path)
                file_contents.append(extracted_text)

        if text:
            logger.info(f"Received text input: {text[:100]}...")
            file_contents.append(text)

        if not file_contents:
            raise HTTPException(status_code=400, detail="No files or text provided")

        classification_result = two_step_classifier.predict(file_contents)
        logger.info(f"Text classified: {classification_result}")
        print(classification_result)
        return {
            "classification": classification_result["probabilities"],
            "resemblance": classification_result["resemblance"]
           
        }

    except Exception as e:
        for temp_file_path in temp_file_paths:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        logger.error(f"Error processing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
    
    finally:
        for temp_file_path in temp_file_paths:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info(f"Temporary file {temp_file_path} removed.")
