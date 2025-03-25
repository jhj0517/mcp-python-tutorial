from tutorial_app import create_mcp_server

if __name__ == "__main__":

    mcp = create_mcp_server()    
    mcp.run()

# Instance for dev mode
app = create_mcp_server()    