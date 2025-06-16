from fastapi import FastAPI, Request
import requests
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

app = FastAPI()

# === Configurar logger para Application Insights ===
logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"))
)
logger.setLevel(logging.INFO)

# === Configuración de HubSpot ===
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
        email = body.get("email")
        calificacion = body.get("calificacion")

        logger.info(f"Petición recibida con email {email} y calificación: {calificacion}")

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
                contact_id = results[0]["id"]
                update_url = f"{HUBSPOT_URL}/{contact_id}"
                update_payload = {
                    "properties": {
                        "calificacion": calificacion
                    }
                }
                update_response = requests.patch(update_url, headers=HEADERS, json=update_payload)
                return {
                    "status": "ok",
                    "hubspot_status": update_response.status_code,
                    "hubspot_response": update_response.json()
                }

        return {"status": "not_found"}

    except Exception as e:
        logger.error(f"Error procesando lead: {str(e)}")
        return {"status": "error", "detail": str(e)}
