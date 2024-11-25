from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import mongo
from app.models import User
from bson import ObjectId
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.get_by_username(request.form['username'])
        if user and user.check_password(request.form['password']):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/books')
@login_required
def books():
    books_list = list(mongo.db.books.find())
    print("Books from database:", books_list)  # Debug print
    return render_template('books.html', books=books_list)

@main.route('/book/borrow/<book_id>')
@login_required
def borrow_book(book_id):
    try:
        book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
        if not book or book['available'] <= 0:
            flash('Book not available')
            return redirect(url_for('main.books'))
        
        borrow_record = {
            'user_id': ObjectId(current_user.get_id()),
            'book_id': ObjectId(book_id),
            'borrow_date': datetime.utcnow(),
            'returned': False
        }
        
        mongo.db.borrow_records.insert_one(borrow_record)
        mongo.db.books.update_one(
            {'_id': ObjectId(book_id)},
            {'$inc': {'available': -1}}
        )
        
        flash('Book borrowed successfully!')
    except Exception as e:
        flash('Error borrowing book')
        
    return redirect(url_for('main.books'))

@main.route('/my-books')
@login_required
def my_books():
    try:
        borrowed_books = list(mongo.db.borrow_records.aggregate([
            {
                '$match': {
                    'user_id': ObjectId(current_user.get_id()),
                    'returned': False
                }
            },
            {
                '$lookup': {
                    'from': 'books',
                    'localField': 'book_id',
                    'foreignField': '_id',
                    'as': 'book'
                }
            },
            {
                '$unwind': '$book'
            }
        ]))
        return render_template('my_books.html', borrowed_books=borrowed_books)
    except Exception as e:
        flash('Error retrieving borrowed books')
        return redirect(url_for('main.index'))

@main.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))
    
    books_list = list(mongo.db.books.find())
    print("Admin books from database:", books_list)  # Debug print
    return render_template('admin.html', books=books_list)

@main.route('/admin/book/add', methods=['POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('main.index'))
    
    book = {
        'title': request.form.get('title'),
        'author': request.form.get('author'),
        'isbn': request.form.get('isbn'),
        'quantity': int(request.form.get('quantity', 1)),
        'available': int(request.form.get('quantity', 1))
    }
    
    try:
        result = mongo.db.books.insert_one(book)
        print("Book added with ID:", result.inserted_id)  # Debug print
        flash('Book added successfully!')
    except Exception as e:
        print("Error adding book:", str(e))  # Debug print
        flash('Error adding book. ISBN might be duplicate.')
    
    return redirect(url_for('main.admin'))

@main.route('/admin/book/edit/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))
    
    book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    if not book:
        flash('Book not found.')
        return redirect(url_for('main.admin'))
    
    if request.method == 'POST':
        updated_book = {
            'title': request.form.get('title'),
            'author': request.form.get('author'),
            'isbn': request.form.get('isbn'),
            'quantity': int(request.form.get('quantity', 1)),
            'available': int(request.form.get('available', 1))
        }
        
        try:
            mongo.db.books.update_one(
                {'_id': ObjectId(book_id)},
                {'$set': updated_book}
            )
            flash('Book updated successfully!')
            return redirect(url_for('main.admin'))
        except Exception as e:
            flash('Error updating book.')
    
    return render_template('edit_book.html', book=book)

@main.route('/admin/book/delete/<book_id>')
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))
    
    try:
        mongo.db.books.delete_one({'_id': ObjectId(book_id)})
        flash('Book deleted successfully!')
    except Exception as e:
        flash('Error deleting book.')
    
    return redirect(url_for('main.admin'))