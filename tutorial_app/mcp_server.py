from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import json
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts import base

from .database import get_db_session, seed_database, User, Post
from .database.connection import db_operation


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
        dependencies=["mcp[cli]", "sqlalchemy", "aiosqlite", "faker"],
        lifespan=app_lifespan
    )
    
    @mcp.resource("users://all")
    @db_operation
    def get_all_users(session=None) -> str:
        """Get all users from the database"""
        users = session.query(User).all()
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
        return json.dumps({"success": True, "users": user_list}, ensure_ascii=False)
    
    @mcp.resource("users://{user_id}/profile")
    @db_operation
    def get_user_profile(user_id: int, session=None) -> str:
        """Get user profile by user ID"""
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return json.dumps({"error": f"User with ID {user_id} not found"}, ensure_ascii=False)
        
        return json.dumps({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "post_count": len(user.posts)
            }
        }, ensure_ascii=False)
    
    @mcp.resource("posts://all")
    @db_operation
    def get_all_posts(session=None) -> str:
        """Get all posts from the database"""
        posts = session.query(Post).all()
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
        return json.dumps({"success": True, "posts": post_list}, ensure_ascii=False)
    
    @mcp.resource("posts://{post_id}")
    @db_operation
    def get_post_by_id(post_id: int, session=None) -> str:
        """Get post by ID"""
        post = session.query(Post).filter(Post.id == post_id).first()
        if not post:
            return json.dumps({"error": f"Post with ID {post_id} not found"}, ensure_ascii=False)
        
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
        }, ensure_ascii=False)
    
    @mcp.tool()
    @db_operation
    def create_user(username: str, email: str, session=None) -> str:
        """Create a new user with the given username and email"""
        # Check if username or email already exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return json.dumps({
                "error": "Username or email already exists"
            }, ensure_ascii=False)
        
        # Create new user
        user = User(username=username, email=email)
        session.add(user)
        session.flush()  # Flush to get the ID without committing
        
        return json.dumps({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            }
        }, ensure_ascii=False)
    
    @mcp.tool()
    @db_operation
    def create_post(title: str, content: str, user_id: int, session=None) -> str:
        """Create a new post with the given title, content, and user ID"""
        # Check if user exists
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return json.dumps({
                "error": f"User with ID {user_id} not found"
            }, ensure_ascii=False)
        
        # Create new post
        post = Post(title=title, content=content, user_id=user_id)
        session.add(post)
        session.flush()  # Flush to get the ID without committing
        
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
        }, ensure_ascii=False)
    
    @mcp.tool()
    @db_operation
    def search_posts(query: str, session=None) -> str:
        """Search posts by title or content"""
        posts = session.query(Post).filter(
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
            "success": True,
            "query": query,
            "result_count": len(post_list),
            "posts": post_list
        }, ensure_ascii=False)
    
    @mcp.prompt()
    def user_profile_analysis(username: str) -> str:
        """Prompt for analyzing a user's profile and posts"""
        return json.dumps({
            "success": True,
            "prompt": f"""
            Analyze the profile and posts of user "{username}".
            
            1. What are the main topics they write about?
            2. What is their writing style?
            3. How active are they based on post frequency?
            4. Provide some suggestions for content they might be interested in creating.
            """
        }, ensure_ascii=False)
    
    @mcp.prompt()
    def post_feedback(post_id: int) -> str:
        """Interactive prompt for providing feedback on a post"""
        return json.dumps({
            "success": True,
            "messages": [
                {"role": "user", "content": f"I'd like feedback on post with ID {post_id}"},
                {"role": "assistant", "content": "I'll help analyze this post. What specific aspects would you like feedback on?"},
                {"role": "user", "content": "I'm interested in the clarity, engagement potential, and grammar."},
                {"role": "assistant", "content": "I'll analyze those aspects. Let me retrieve the post content first."}
            ]
        }, ensure_ascii=False)
    
    return mcp 