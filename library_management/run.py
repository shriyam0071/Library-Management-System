from app import create_app, mongo
from app.models import User

app = create_app()

def init_db():
    with app.app_context():
        # Create admin user if it doesn't exist
        admin = mongo.db.users.find_one({'username': 'admin'})
        if not admin:
            User.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_admin=True
            )
            
            # Add some sample books
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
                },
                {
                    'title': 'Database Design',
                    'author': 'Jane Doe',
                    'isbn': '1234567890125',
                    'quantity': 3,
                    'available': 3
                }
            ]
            mongo.db.books.insert_many(sample_books)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)