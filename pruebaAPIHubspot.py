from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
HUBSPOT_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

@app.post("/nuevo-lead")
async def nuevo_lead(request: Request):
    body = await request.json()

    nombre = body.get("nombre")
    email = body.get("email")
    telefono = body.get("telefono")
    calificacion = body.get("calificacion")  # ← JSON enviado por Sintonai

    payload = {
        "properties": {
            "firstname": nombre,
            "email": email,
            "phone": telefono,
            "calificacion": calificacion
        }
    }

    res = requests.post(HUBSPOT_URL, headers=HEADERS, json=payload)

    return {
        "hubspot_status": res.status_code,
        "hubspot_response": res.json()
    }
