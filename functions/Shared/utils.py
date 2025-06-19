import logging
from azure.functions import HttpRequest, HttpResponse

def parse_request(req: HttpRequest) -> dict:
    try:
        return req.get_json()
    except ValueError:
        logging.error("Invalid JSON in request.")
        return {}

def create_response(body: dict, status_code: int = 200) -> HttpResponse:
    return HttpResponse(
        body=str(body),
        status_code=status_code,
        mimetype="application/json"
    )
