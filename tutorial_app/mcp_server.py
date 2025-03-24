from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import json
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts import base

from .database import get_db_session, seed_database, User, Post


@dataclass
class AppContext:
    """Application context available across the MCP server"""
    initialized: bool = False


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    print("Initializing MCP Tutorial App...")
    
    # Add mock data to the database
    seed_database()
    
    app_context = AppContext(initialized=True)
    try:
        yield app_context
    finally:
        print("Shutting down MCP Tutorial App...")


def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(
        "MCP Tutorial App", 
        dependencies=["sqlalchemy", "fastapi", "httpx", "faker"],
        lifespan=app_lifespan
    )
    
    @mcp.resource("users://all")
    def get_all_users() -> str:
        """Get all users from the database"""
        with get_db_session() as db:
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
            return json.dumps(user_list, indent=2)
    
    @mcp.resource("users://{user_id}/profile")
    def get_user_profile(user_id: int) -> str:
        """Get user profile by user ID"""
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return json.dumps({"error": f"User with ID {user_id} not found"})
            
            return json.dumps({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "post_count": len(user.posts)
            }, indent=2)
    
    @mcp.resource("posts://all")
    def get_all_posts() -> str:
        """Get all posts from the database"""
        with get_db_session() as db:
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
            return json.dumps(post_list, indent=2)
    
    @mcp.resource("posts://{post_id}")
    def get_post_by_id(post_id: int) -> str:
        """Get post by ID"""
        with get_db_session() as db:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return json.dumps({"error": f"Post with ID {post_id} not found"})
            
            return json.dumps({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at.isoformat(),
                "author": {
                    "id": post.author.id,
                    "username": post.author.username
                }
            }, indent=2)
    
    # Register tools
    @mcp.tool()
    def create_user(username: str, email: str) -> str:
        """Create a new user with the given username and email"""
        with get_db_session() as db:
            # Check if username or email already exists
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return json.dumps({
                    "error": "Username or email already exists"
                })
            
            # Create new user
            user = User(username=username, email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return json.dumps({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at.isoformat()
                }
            })
    
    @mcp.tool()
    def create_post(title: str, content: str, user_id: int) -> str:
        """Create a new post with the given title, content, and user ID"""
        with get_db_session() as db:
            # Check if user exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return json.dumps({
                    "error": f"User with ID {user_id} not found"
                })
            
            # Create new post
            post = Post(title=title, content=content, user_id=user_id)
            db.add(post)
            db.commit()
            db.refresh(post)
            
            return json.dumps({
                "success": True,
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
            })
    
    @mcp.tool()
    def search_posts(query: str) -> str:
        """Search posts by title or content"""
        with get_db_session() as db:
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
            
            return json.dumps({
                "query": query,
                "result_count": len(post_list),
                "posts": post_list
            })
    
    # Register prompts
    @mcp.prompt()
    def user_profile_analysis(username: str) -> str:
        """Prompt for analyzing a user's profile and posts"""
        return f"""
        Analyze the profile and posts of user "{username}".
        
        1. What are the main topics they write about?
        2. What is their writing style?
        3. How active are they based on post frequency?
        4. Provide some suggestions for content they might be interested in creating.
        """
    
    @mcp.prompt()
    def post_feedback(post_id: int) -> list[base.Message]:
        """Interactive prompt for providing feedback on a post"""
        return [
            base.UserMessage(f"I'd like feedback on post with ID {post_id}"),
            base.AssistantMessage("I'll help analyze this post. What specific aspects would you like feedback on?"),
            base.UserMessage("I'm interested in the clarity, engagement potential, and grammar."),
            base.AssistantMessage("I'll analyze those aspects. Let me retrieve the post content first."),
        ]
    
    return mcp 