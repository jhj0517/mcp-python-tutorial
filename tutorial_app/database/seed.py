from .connection import get_db_session, create_tables, db_operation
from .models import User, Post
import random
from faker import Faker

fake = Faker()

@db_operation
def _seed_data_if_needed(session=None):
    """Seed the database with initial data if it's empty"""
    existing_users = session.query(User).count()
    if existing_users > 0:
        print("Database already has data, skipping seed")
        return False
    
    users = []
    # Create users
    for i in range(10):
        user = User(
            username=fake.user_name(),
            email=fake.email()
        )
        session.add(user)
        users.append(user)
    
    session.flush()
    
    for user in users:
        for _ in range(random.randint(1, 5)):
            post = Post(
                title=fake.sentence(),
                content=fake.paragraph(nb_sentences=5),
                user_id=user.id
            )
            session.add(post)
    
    return True

def seed_database():
    """Populate the database with sample data"""
    create_tables()
    result = _seed_data_if_needed()
    
    if isinstance(result, str) and "error" in result:
        print(f"Error seeding database: {result}")
    elif result:
        print("Database seeded with mock data")

if __name__ == "__main__":
    seed_database() 