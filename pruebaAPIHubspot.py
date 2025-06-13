from fastapi import FastAPI, Request
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
HUBSPOT_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

@app.post("/nuevo-lead")
async def nuevo_lead(request: Request):
    data = await request.json()

    nombre = data.get("nombre")
    email = data.get("email")
    telefono = data.get("telefono")

    # Extrae todos los campos extra como calificación dinámica
    calificacion_dinamica = {
        k: v for k, v in data.items()
        if k not in ["nombre", "email", "telefono"]
    }

    payload = {
        "properties": {
            "firstname": nombre,
            "email": email,
            "phone": telefono,
            "calificacion": json.dumps(calificacion_dinamica)
        }
    }

    response = requests.post(HUBSPOT_URL, headers=HEADERS, json=payload)

    return {
        "status": response.status_code,
        "hubspot": response.json()
    }
