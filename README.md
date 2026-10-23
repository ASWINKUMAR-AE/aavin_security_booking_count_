# Aavin Security Booking Count

Aavin security booking tracking with OCR-based data capture and milk-quantity processing.

## Components

- `config/`: Django project configuration.
- `ocr/`: the OCR application and service.

## Django setup with WSL

```bash
cd "/mnt/d/aavin ocr milk wuantity"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## PostgreSQL environment

Copy `.env.example` to `.env`, then set `SECRET_KEY` and the `DB_*` PostgreSQL
values. The `.env` file is ignored by Git.

## Branches

| Branch | Description |
| --- | --- |
| `main` | Stable project branch |
| `ocr`  | OCR-based booking tracking feature development |
