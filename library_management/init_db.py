from app import create_app, mongo
from app.models import User

app = create_app()

def init_db():
    with app.app_context():
        # Clear existing data
        mongo.db.users.delete_many({})
        mongo.db.books.delete_many({})
        mongo.db.borrow_records.delete_many({})

        # Create indexes
        mongo.db.users.create_index('username', unique=True)
        mongo.db.users.create_index('email', unique=True)
        mongo.db.books.create_index('isbn', unique=True)

        # Create admin user
        User.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_admin=True
        )

        # Add sample books
        sample_books = [
            {
                'title': 'Python Programming',
                'author': 'John Smith',
                'isbn': '1234567890123',
                'quantity': 2,
                'available': 2
            },
            {
                'title': 'Flask Web Development',
                'author': 'Miguel Grinberg',
                'isbn': '1234567890124',
                'quantity': 1,
                'available': 1
            }
        ]
        mongo.db.books.insert_many(sample_books)

if __name__ == '__main__':
    init_db() 