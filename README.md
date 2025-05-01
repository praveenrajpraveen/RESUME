
This script extracts structured data from unstructured resume PDFs using a hybrid approach combining traditional regex, NLP (spaCy), and OCR (Tesseract for image-based PDFs). It outputs the parsed information in a JSON format along with confidence scores for each field.

- Full Name  
- Email Address  
- Phone Number  
- LinkedIn URL  
- Skills  
- Education (Degree, Institution, Year)  
- Work Experience (Company, Title, Duration, Description)  
- Certifications  
- Projects  

Each field is returned with a confidence score (0.0 to 1.0).


1. **PDF Parsing**:  
   - For text-based PDFs: `pdfplumber`
   - For image-based PDFs: `pdf2image` + `pytesseract` (OCR fallback)

2. **Information Extraction**:  
   - Regex for email, phone, LinkedIn, certifications, etc.  
   - `spaCy` NLP for name and named entities  
   - Custom logic for skills, experience, and date normalization  

3. **Confidence Scoring**:  
   - Heuristically set based on match strength or presence of reliable patterns.

4. **Fallback Logging**:  
   - If fields are missing, they are returned as `null` and logged via the `logging` module.



- `pdfplumber` – for extracting text from PDFs  
- `pdf2image` & `pytesseract` – for OCR fallback  
- `spacy` – for NER-based name extraction  
- `dateparser` – to handle flexible date formats  
- `re` – for pattern matching (regex)  
- `logging`, `json` – for debug/info logging and structured output  

- Assumes resumes are mostly in English.
- Skills list is hardcoded but can be expanded.
- Accuracy may vary depending on resume formatting and OCR quality.
- Projects and certifications are detected with basic keyword matching.
- Does not classify job descriptions or use deep learning models (to keep it lightweight).
- Only standard PDF and image-based PDFs are supported (no docx or scans with poor quality).
- 
Make sure you have Tesseract installed and added to your system PATH.

pip install -r requirements.txt

# Run the parser
python app.py
