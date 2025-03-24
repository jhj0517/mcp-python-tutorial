# MCP Python Tutorial
Tutorial app for MCP in Python with simple local DB with mocking data

## Installation & Run

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run MCP server:
```bash
mcp dev app.py
```

4. Default port for MCP server is `5173`. Access to `http://localhost:5173`.

## MCP Features
This tutorial app demonstrates core MCP concepts:

### Resources 
Basically, `@mcp.resource()` is about the agent "getting" the resource, just like `GET` in the REST API.
- `users://all` - Get all users
- `users://{user_id}/profile` - Get a user's profile
- `posts://all` - Get all posts
- `posts://{post_id}` - Get a post by ID

### Tools
`@mcp.tool()` is about the agent "generating" the new resource, just like `POST` in the REST API.
- `create_user` - Create a new user
- `create_post` - Create a new post
- `search_posts` - Search posts by title or content

### Prompts
`@mcp.prompt()` is just a reusable template to interact with LLM conveniently.
- `user_profile_analysis` - Generate analysis of a user's profile
- `post_feedback` - Interactive prompt for post feedback

For more annotations, please read : https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#core-concepts
