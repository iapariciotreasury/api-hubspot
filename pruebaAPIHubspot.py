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
    calificacion = body.get("calificacion")

    # Buscar contacto por email
    search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    search_body = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            }]
        }]
    }

    search_response = requests.post(search_url, headers=HEADERS, json=search_body)

    if search_response.status_code == 200:
        results = search_response.json().get("results", [])
        if results:
            # Contacto encontrado → actualizar
            contact_id = results[0]["id"]
            update_url = f"{HUBSPOT_URL}/{contact_id}"
            update_payload = {
                "properties": {
                    "calificacion": calificacion
                }
            }
            update_response = requests.patch(update_url, headers=HEADERS, json=update_payload)
            return {
                "status": "updated",
                "contact_id": contact_id,
                "response": update_response.json()
            }

    # Contacto no encontrado → crear
    create_payload = {
        "properties": {
            "firstname": nombre,
            "email": email,
            "phone": telefono,
            "calificacion": calificacion
        }
    }
    create_response = requests.post(HUBSPOT_URL, headers=HEADERS, json=create_payload)

    return {
        "status": "created",
        "response": create_response.json()
    }
