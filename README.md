# Aavin OCR Milk Quantity

Django application foundation for extracting and processing milk-quantity data from images or documents.

## Setup with WSL

```bash
cd "/mnt/d/aavin ocr milk wuantity"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The OCR functionality belongs in the separate `ocr` Django app.
