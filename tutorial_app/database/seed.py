from .connection import get_db_session, create_tables
from .models import User, Post
import random
from faker import Faker

fake = Faker()

def seed_database():
    """Populate the database with sample data"""
    create_tables()
    
    users = []
    with get_db_session() as db:
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already has data, skipping seed")
            return
        
        for i in range(10):
            user = User(
                username=fake.user_name(),
                email=fake.email()
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        
        for user in users:
            for _ in range(random.randint(1, 5)):
                post = Post(
                    title=fake.sentence(),
                    content=fake.paragraph(nb_sentences=5),
                    user_id=user.id
                )
                db.add(post)
        
        db.commit()
    
    print("Database seeded with mocking data")

if __name__ == "__main__":
    seed_database() 