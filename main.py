# main.py
import os
import contextlib
from typing import Any, Dict
from urllib.parse import quote

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
GEOCODER_BASE = os.getenv("GEOCODER_BASE", "http://mb.georepublic.info/")

# Geocode (address in path)
GEOCODER_GEOCODE_PREFIX = os.getenv(
    "GEOCODER_GEOCODE_PREFIX",
    "/geocoderService/service/geocode/geojson/"
)

# Reverse geocode (lon,lat in path)
GEOCODER_REVERSE_PREFIX = os.getenv(
    "GEOCODER_REVERSE_PREFIX",
    "/geocoderService/service/reversegeocode/json/"
)

# Shortest path (Dijkstra) endpoint (query params)
ROUTER_PREFIX = os.getenv(
    "ROUTER_PREFIX",
    "/pgrServer/api/latlng/dijkstra"
)

REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10.0"))

CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost,http://127.0.0.1"
).split(",")

CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"

# -----------------------------------------------------------------------------
# MCP server
# -----------------------------------------------------------------------------
mcp = FastMCP("Location Services (Streamable HTTP)")
# Avoid /mcp/mcp by making the internal path live at the mount point
mcp.settings.streamable_http_path = "/"

# -----------------------------------------------------------------------------
# Tools
# -----------------------------------------------------------------------------
@mcp.tool()
async def geocode(address: str) -> Dict[str, Any]:
    """
    Geocode a Japanese address.

    Returns JSON if available; otherwise {"raw": "..."}.
    """
    base = GEOCODER_BASE.rstrip("/")
    prefix = "/" + GEOCODER_GEOCODE_PREFIX.strip("/") + "/"
    encoded_addr = quote(address, safe="")
    url = f"{base}{prefix}{encoded_addr}"

    headers = {"Accept": "application/json, text/plain;q=0.8, */*;q=0.5"}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        if "application/json" in resp.headers.get("content-type", ""):
            return resp.json()
        return {"raw": resp.text}

@mcp.tool()
async def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """
    Reverse geocode using a Latitude and Longitude coordinates as parameters.
    """
    base = GEOCODER_BASE.rstrip("/")
    prefix = "/" + GEOCODER_REVERSE_PREFIX.strip("/") + "/"
    url = f"{base}{prefix}{lon},{lat}"

    headers = {"Accept": "application/json, text/plain;q=0.8, */*;q=0.5"}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        if "application/json" in resp.headers.get("content-type", ""):
            return resp.json()
        return {"raw": resp.text}

@mcp.tool()
async def shortest_path(
    source_lat: float,
    source_lon: float,
    target_lat: float,
    target_lon: float
) -> Dict[str, Any]:
    """
    Find the shortest path (Dijkstra) between two coordinates.
    NOTE: Service expects X=longitude, Y=latitude (lon, lat).
    """
    base = GEOCODER_BASE.rstrip("/")
    path = "/" + ROUTER_PREFIX.strip("/")

    url = f"{base}{path}"
    params = {
        # X = longitude, Y = latitude
        "source_x": source_lon,
        "source_y": source_lat,
        "target_x": target_lon,
        "target_y": target_lat,
    }

    headers = {"Accept": "application/json, text/plain;q=0.8, */*;q=0.5"}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        if "application/json" in resp.headers.get("content-type", ""):
            return resp.json()
        return {"raw": resp.text}

# -----------------------------------------------------------------------------
# FastAPI app + MCP lifecycle (prevents 500s)
# -----------------------------------------------------------------------------
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(title="JP Geocoder MCP Server", lifespan=lifespan)

# -----------------------------------------------------------------------------
# CORS (for browser-based MCP clients; expose session header)
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ALLOWED_ORIGINS if o.strip()],
    allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
    allow_headers=["*"],
    expose_headers=[
        "Mcp-Session-Id",
        "Content-Type",
        "Cache-Control",
    ],
    allow_credentials=CORS_ALLOW_CREDENTIALS,
)

# -----------------------------------------------------------------------------
# Mount MCP Streamable HTTP transport at /mcp
# -----------------------------------------------------------------------------
app.mount("/mcp", mcp.streamable_http_app())

# Health check
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}