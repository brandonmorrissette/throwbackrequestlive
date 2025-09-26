import os
import base64
import requests
from urllib.parse import urljoin, urlencode, urlparse

HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate",
    "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
}

def handler(event, context):
    fargate_url = os.environ.get("FARGATE_URL")
    if not fargate_url:
        return {"statusCode": 500, "body": "FARGATE_URL not set"}
    
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("path", event.get("rawPath", "/"))
    qs = event.get("queryStringParameters") or {}
    raw_qs = urlencode(qs)
    target = urljoin(fargate_url, path)
    if raw_qs:
        target = f"{target}?{raw_qs}"
    
    headers = {k: v for k, v in (event.get("headers") or {}).items()
               if k and k.lower() not in HOP_BY_HOP and k.lower() != "host"}

    if source := event.get("requestContext", {}).get("http", {}).get("sourceIp"):
        xff = headers.get("X-Forwarded-For")
        headers["X-Forwarded-For"] = f"{xff}, {source}" if xff else source

    body = event.get("body")
    data = base64.b64decode(body) if event.get("isBase64Encoded") else body or None
    
    resp = requests.request(method, target, headers=headers, data=data, stream=True, allow_redirects=False)
    
    resp_headers = {k: v for k, v in resp.raw.headers.items()
                    if k.lower() not in HOP_BY_HOP}
    
    try:
        text = resp.content.decode("utf-8")
        is_b64 = False
        body_out = text
    except:
        is_b64 = True
        body_out = base64.b64encode(resp.content).decode("ascii")

    return {
        "statusCode": resp.status_code,
        "headers": resp_headers,
        "body": body_out,
        "isBase64Encoded": is_b64
    }
