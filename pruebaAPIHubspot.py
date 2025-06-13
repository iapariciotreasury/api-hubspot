from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

# Token de HubSpot (lo ideal es usar variables de entorno en producción)
HUBSPOT_TOKEN = "pat-na1-11a676c3-11f6-4d29-83dc-d15c3f0544f6"
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
    calificacion = body.get("calificacion")

    # Si no quieres descomponer "calificacion", lo metes todo en un campo tipo texto
    payload = {
        "properties": {
            "firstname": nombre,
            "email": email,
            "phone": telefono,
            "calificacion": str(calificacion)  # Como texto
        }
    }

    res = requests.post(HUBSPOT_URL, headers=HEADERS, json=payload)

    return {
        "hubspot_status": res.status_code,
        "hubspot_response": res.json()
    }
