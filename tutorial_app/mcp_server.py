from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP

from .database import seed_database, User, Post
from .database.connection import db_handler, json_response


@dataclass
class AppContext:
    """Application context available across the MCP server"""
    initialized: bool = False


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    try:
        print("Initializing MCP Tutorial App...")
        # Add mock data to the database
        seed_database()
        app_context = AppContext(initialized=True)
        yield app_context
    except Exception as e:
        print(f"Error during initialization: {e}")
    finally:
        print("Shutting down MCP Tutorial App...")


def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(
        "MCP Tutorial App", 
        dependencies=["mcp[cli]", "sqlalchemy", "aiosqlite", "faker"],
        lifespan=app_lifespan
    )
    
    @mcp.resource("users://all")
    @db_handler
    def get_all_users(db) -> Dict:
        """Get all users from the database"""
        users = db.query(User).all()
        user_list = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "post_count": len(user.posts)
            }
            for user in users
        ]
        return {"users": user_list}
    
    @mcp.resource("users://{user_id}/profile")
    @db_handler
    def get_user_profile(user_id: int, db) -> Dict:
        """Get user profile by user ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": f"User with ID {user_id} not found"}
        
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "post_count": len(user.posts)
            }
        }
    
    @mcp.resource("posts://all")
    @db_handler
    def get_all_posts(db) -> Dict:
        """Get all posts from the database"""
        posts = db.query(Post).all()
        post_list = [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "username": post.author.username
                }
            }
            for post in posts
        ]
        return {"posts": post_list}
    
    @mcp.resource("posts://{post_id}")
    @db_handler
    def get_post_by_id(post_id: int, db) -> Dict:
        """Get post by ID"""
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return {"error": f"Post with ID {post_id} not found"}
        
        return {
            "post": {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "username": post.author.username
                }
            }
        }
    
    @mcp.tool()
    @db_handler
    def create_user(username: str, email: str, db) -> Dict:
        """Create a new user with the given username and email"""
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return {"error": "Username or email already exists"}
        
        # Create new user
        user = User(username=username, email=email)
        db.add(user)
        # No need to commit here, the decorator handles it
        db.refresh(user)
        
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            }
        }
    
    @mcp.tool()
    @db_handler
    def create_post(title: str, content: str, user_id: int, db) -> Dict:
        """Create a new post with the given title, content, and user ID"""
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": f"User with ID {user_id} not found"}
        
        # Create new post
        post = Post(title=title, content=content, user_id=user_id)
        db.add(post)
        # No need to commit here, the decorator handles it
        db.refresh(post)
        
        return {
            "post": {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "username": post.author.username
                }
            }
        }
    
    @mcp.tool()
    @db_handler
    def search_posts(query: str, db) -> Dict:
        """Search posts by title or content"""
        posts = db.query(Post).filter(
            (Post.title.ilike(f"%{query}%")) | 
            (Post.content.ilike(f"%{query}%"))
        ).all()
        
        post_list = [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "username": post.author.username
                }
            }
            for post in posts
        ]
        
        return {
            "query": query,
            "result_count": len(post_list),
            "posts": post_list
        }
    
    @mcp.prompt()
    @json_response
    def user_profile_analysis(username: str) -> Dict:
        """Prompt for analyzing a user's profile and posts"""
        return {
            "prompt": f"""
            Analyze the profile and posts of user "{username}".
            
            1. What are the main topics they write about?
            2. What is their writing style?
            3. How active are they based on post frequency?
            4. Provide some suggestions for content they might be interested in creating.
            """
        }
    
    @mcp.prompt()
    @json_response
    def post_feedback(post_id: int) -> Dict:
        """Interactive prompt for providing feedback on a post"""
        return {
            "messages": [
                {"role": "user", "content": f"I'd like feedback on post with ID {post_id}"},
                {"role": "assistant", "content": "I'll help analyze this post. What specific aspects would you like feedback on?"},
                {"role": "user", "content": "I'm interested in the clarity, engagement potential, and grammar."},
                {"role": "assistant", "content": "I'll analyze those aspects. Let me retrieve the post content first."}
            ]
        }
    
    return mcp 