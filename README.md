# MCP with StreamingHTTP Transport

This is a test application to create a remote MCP Server
that uses the new StreamingHTTP transport protocol.


### Setup and Running the Application

Run the `setup_venv.sh` to create a virtual environment,
download the necessary Python libraries, and start the
web service. 

Once the web service is running, the MCP Inspector web 
application can be used to test the MVC services using the 
Streaming HTTP transport protocol.

### Restarting the Web Service

To restart the web service, do: 

```commandline
uvicorn main:app --host 0.0.0.0 --port 8000
```
### Claude Desktop Configuration Parameters

The JSON parameters below can be used to configure
the MCP services for LLM usage. 

```json
{
  "mcpServers": {
    "geolonia-streaminghttp": {
      "transport": { "type": "streaming-http", "url": "http://localhost:8000/mcp" },
      "env": {
        "GEOCODER_BASE": "http://mb.georepublic.info",
        "GEOCODER_PATH": "/"
      }
    }
  }
}
```

The current version of Claude Desktop though does not 
support yet a direct transport, and will need an 
external application like `uv` to connect to the
MCP service. 

```json
{
  "mcpServers": {
    "geolonia-streaminghttp": {
      "command": "/opt/homebrew/bin/uvx",
      "args": [
        "mcp-proxy",
        "http://localhost:8000/mcp",
        "--transport=streamablehttp"
      ]
    }
  }
}
```