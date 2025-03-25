# MCP Python Tutorial
Tutorial app for MCP in Python with simple local DB with mocking data

## Installation & Run

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run MCP server as dev mode:
```bash
mcp dev localdb_app.py
```

4. Default port for MCP server is `5173`. Access to `http://localhost:5173`.

## MCP Features
This tutorial app demonstrates core MCP concepts.<br>
You can check annotation-per-role in [tutorial_app/mcp_server.py](https://github.com/jhj0517/mcp-python-tutorial/blob/main/tutorial_app/mcp_server.py):

### `@mcp.resource`
Basically, this annotation is about the agent "getting" the resource, just like `GET` in the RESTAPI.
- `users://all` - Get all users
- `users://{user_id}/profile` - Get a user's profile
- `posts://all` - Get all posts
- `posts://{post_id}` - Get a post by ID

### `@mcp.tool`
This is about the agent "generating" the new resource, just like `POST` in the RESTAPI.
- `create_user` - Create a new user
- `create_post` - Create a new post
- `search_posts` - Search posts by title or content

### `@mcp.prompt`
This is just a reusable template to interact with LLM conveniently.
- `user_profile_analysis` - Generate analysis of a user's profile
- `post_feedback` - Interactive prompt for post feedback

> [!NOTE]
> For more annotations, please read : https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#core-concepts

## Connecting to Client

Once you've set up the MCP server, you need an LLM client that will use your MCP server to build your agent. 
The following guide will help you connect with [Claude Desktop](https://claude.ai/download) as your client.

1. Claude Desktop uses `uv` to install MCP server dependencies. First, install `uv`:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Install MCP server dependencies using `uv`:
```bash
# Create virtual environment and activate it
uv venv
.venv\Scripts\activate

uv pip install -r requirements.txt
```

3. Download Claude Desktop from:
- https://claude.ai/download

4. Locate or create the `claude_desktop_config.json` file. The location varies by OS:
- Windows:
```
C:\Users\%USER%\AppData\Roaming\Claude\claude_desktop_config.json
```
- MacOS/Linux:
```
~/Library/Application\ Support/Claude/claude_desktop_config.json
```

5. Add the `mcpServers` attribute to your `claude_desktop_config.json`:
```json
{
    "mcpServers": {
        "local_db": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/weather",
                "run",
                "localdb_app.py"
            ]
        }
    }
}
```
Note: You can deploy multiple MCP servers, each with its own dedicated concerns and expertise. <br>
This separation of concerns is better than implementing everything in a single MCP server.

6. Restart Claude Desktop.
