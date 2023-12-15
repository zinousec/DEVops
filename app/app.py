import math
from flask import Flask, render_template, request, abort, send_from_directory
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import distinct, desc

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
from book import bp as book_bp
from tools import BooksFilter

app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)

init_login_manager(app)

from models import *

PER_PAGE = 10

def search_params():
    title = request.args.get('title', '')
    genres_list = request.args.getlist('genre_id')
    years_list = request.args.getlist('year')
    amount_from = request.args.get('amount_from', '')
    amount_to = request.args.get('amount_to', '')
    author = request.args.get('author', '')
    return {
        'title': title,
        'genre_id': genres_list,
        'year': years_list,
        'amount_from': amount_from,
        'amount_to': amount_to,
        'author': author
    }

@app.route('/')
def index():
    genres = Genre.query.all()
    book_genre = Books_has_Genres.query.all()
    books_counter = Book.query.count()
    years = db.session.query(distinct(Book.year)).order_by(desc(Book.year)).all()
    years = [str(year[0]) for year in years]

    page = request.args.get('page', 1, type=int)
    books = db.session.execute(db.select(Book).order_by(desc(Book.year)).limit(PER_PAGE).offset(PER_PAGE * (page - 1))).scalars()
    page_count = math.ceil(books_counter / PER_PAGE)

    title = request.args.get('title', '')
    genres_list = request.args.getlist('genre_id')
    years_list = request.args.getlist('year')
    amount_from = request.args.get('amount_from', '')
    amount_to = request.args.get('amount_to', '')
    author = request.args.get('author', '')
    genres_list = [int(x) for x in genres_list]
    flag = True
    if books == []:
        flag = False
    rating = Book.rating
    return render_template('index.html', books=books, genres=genres, years=years, book_genre=book_genre, page=page,
        page_count=page_count, rating=rating,
     search_params = search_params(), title=title, genres_list=genres_list, years_list=years_list, amount_from=amount_from, amount_to=amount_to, author=author, flag=flag)
        
@app.route('/media/images/<cover_id>')
def image(cover_id):
    cover = Cover.query.get(cover_id)
    if cover is None:
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], cover.file_name)