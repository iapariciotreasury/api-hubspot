from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

@app.post("/nuevo-lead")
async def nuevo_lead(request: Request):
    body = await request.json()
    email = body.get("email")
    calificacion = body.get("calificacion")

    # Buscar contacto por email
    search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    search_payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            }]
        }],
        "properties": ["email"]
    }
    search_res = requests.post(search_url, headers=HEADERS, json=search_payload)
    results = search_res.json().get("results", [])

    if not results:
        return {"error": "Contacto no encontrado con ese email"}

    contact_id = results[0]["id"]

    # Actualizar campo calificación
    update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    update_payload = {
        "properties": {
            "calificacion": calificacion
        }
    }
    update_res = requests.patch(update_url, headers=HEADERS, json=update_payload)

    return {
        "mensaje": f"Contacto actualizado con calificación: {calificacion}",
        "hubspot_status": update_res.status_code,
        "hubspot_response": update_res.json()
    }
