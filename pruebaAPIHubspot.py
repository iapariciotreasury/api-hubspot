from fastapi import FastAPI, Request
import requests
import os
import logging
import sys

# Configura logging para enviar trazas a Application Insights
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s: %(message)s"
)

app = FastAPI()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
HUBSPOT_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

@app.post("/nuevo-lead")
async def nuevo_lead(request: Request):
    try:
        body = await request.json()
        logging.info(f"Body recibido: {body}")  # <<-- VISUALIZABLE EN APP INSIGHTS

        email = body.get("email")
        calificacion = body.get("calificacion")

        if not email:
            logging.warning("No se proporcionó email en la petición.")
            return {"status": "error", "detail": "Falta el email"}

        # Buscar el contacto por email
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
                contact_id = results[0]["id"]
                update_url = f"{HUBSPOT_URL}/{contact_id}"
                update_payload = {
                    "properties": {
                        "calificacion": calificacion
                    }
                }

                update_response = requests.patch(update_url, headers=HEADERS, json=update_payload)
                logging.info(f"Contacto actualizado: {email} → {calificacion}")
                return {
                    "status": "ok",
                    "hubspot_status": update_response.status_code,
                    "hubspot_response": update_response.json()
                }

            else:
                logging.warning(f"No se encontró contacto con email: {email}")
                return {"status": "not_found"}

        else:
            logging.error(f"Error en búsqueda HubSpot: {search_response.text}")
            return {"status": "error", "detail": "Fallo en búsqueda HubSpot"}

    except Exception as e:
        logging.exception("Error en /nuevo-lead")
        return {"status": "error", "detail": str(e)}
