from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required
from app import db
import os
import bleach
import markdown
from auth import check_rights

bp = Blueprint('book', __name__, url_prefix='/book')

from models import Genre, Book, Books_has_Genres, Cover, Review
from tools import ImageSaver

@bp.route('/new', methods=['GET', 'POST'])
@check_rights('new')
def new():
    if request.method == 'GET':
        genres = Genre.query.all()
        return render_template('book/new.html', genres=genres)
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        publisher = request.form.get('publisher')
        amount = request.form.get('amount')
        year = request.form.get('year')
        description = bleach.clean(request.form.get('description'))
        f = request.files.get('cover_img')
        if f and f.filename:
            try:
                cover_id = ImageSaver(f).save()
                book = Book(title=title, description=description, year=year, publisher=publisher, author=author, amount=amount, cover_id=cover_id)
                db.session.add(book)
                db.session.commit()
                genres = request.form.getlist('genre_id')
                for i in genres:
                    genre_in_db = Books_has_Genres(books_id=book.id, genres_id=i)
                    db.session.add(genre_in_db)
                    db.session.commit()
                flash(f'Книга "{book.title}" успешно добавлена!', 'success')
                return redirect(url_for('index'))
            except:
                flash("Возникла ошибка", "danger")
                return redirect(url_for('book.new'))
        else:
            flash("Возникла ошибка", "danger")
            return redirect(url_for('book.new'))

@bp.route('/show/<int:book_id>')
def show(book_id):
    book = Book.query.get(book_id)
    book.description = markdown.markdown(book.description)
    book_genre = Books_has_Genres.query.all()
    cover_id = book.cover_id
    img = Cover.query.filter_by(id=cover_id).first()
    img = img.url
    if current_user.is_authenticated:
        review = Review.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if review:
            review = markdown.markdown(review.text)
    else:
        review = False

    reviews = Review.query.filter_by(book_id=book_id).all()

    markdown_comments = []
    if reviews:
        for comment in reviews:
            markdown_comments.append({
                'get_user': comment.get_user,
                'rating': comment.rating,
                'text': markdown.markdown(comment.text)
            })
    return render_template('book/show.html', book=book, book_genre=book_genre, img=img, review=review, reviews=markdown_comments)

@bp.route('/delete/<int:book_id>', methods=['POST', 'GET'])
@check_rights('delete')
def delete(book_id):
    if request.method == 'POST':
        book_genres = Books_has_Genres.query.filter_by(books_id=book_id).all()
        for book_genre in book_genres:
            db.session.delete(book_genre)
            db.session.commit()
        book_reviews = Review.query.filter_by(book_id=book_id).all()
        for review in book_reviews:
            db.session.delete(review)
            db.session.commit()
        book = Book.query.filter_by(id=book_id).first()
        try:
            img = Cover.query.filter_by(id=book.cover_id).first()
            if len(Book.query.filter_by(cover_id=book.cover_id).all()) == 1:
                img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images', img.file_name)
                os.remove(img_path)
                db.session.delete(img)
                db.session.commit()
            else:
                db.session.delete(book)
                db.session.commit()
        except:
            pass
        flash(f'Книга успешно удалена!', 'success')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@check_rights('edit')
def edit(book_id):
    book = Book.query.get(book_id)
    genres = Genre.query.all()
    if request.method == 'GET':
        selected_genres = Books_has_Genres.query.filter_by(books_id=book_id).all()
        selected_genres_list = []
        for i in selected_genres:
            selected_genres_list.append(i.genres_id)
        return render_template('book/edit.html', book=book, genres=genres, selected_genres_list=selected_genres_list)
    if request.method == 'POST':
        try:
            book.title = request.form.get('title')
            book.author = request.form.get('author')
            book.publisher = request.form.get('publisher')
            book.amount = request.form.get('amount')
            book.year = request.form.get('year')
            book.description = bleach.clean(request.form.get('description'))
            db.session.commit()
            while Books_has_Genres.query.filter_by(books_id=book_id).first():
                db.session.delete(Books_has_Genres.query.filter_by(books_id=book_id).first())
                db.session.commit()
            selected_genres = request.form.getlist('genre_id')
            for i in selected_genres:
                a = Books_has_Genres(books_id=book_id, genres_id=i)
                db.session.add(a)
                db.session.commit()
            flash(f'Книга "{book.title}" успешно изменена!', 'success')
            return redirect(url_for('index'))
        except:
            flash('Возникла ошибка', 'danger')
            return render_template('book/edit.html', book=book, genres=genres, selected_genres_list=selected_genres_list)


@bp.route('/review/<int:book_id>', methods=['GET', 'POST'])
@login_required
def review(book_id):
    book = Book.query.get(book_id)
    if request.method == 'POST':
        try:
            text = request.form.get('review')
            mark = int(request.form.get('mark'))
            review = Review(rating=mark, text=text, book_id=book_id, user_id=current_user.get_id())
            book.rating_num += 1
            book.rating_sum += int(review.rating)
            db.session.add(review)
            db.session.commit()
            flash(f'Отзыв был успешно добавлен!', 'success')
            return redirect(url_for('book.show', book_id=book.id))
        except:
            flash('Возникла ошибка', 'danger')
            return redirect(url_for('book.show', book_id=book.id))
    if request.method == 'GET':
        return render_template('book/review.html', book=book)

