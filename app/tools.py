from models import Book, Cover
import hashlib
import os
from werkzeug.utils import secure_filename
from app import db, app

class BooksFilter:
    def __init__(self):
        self.query = Book.query

    def perform(self, title='', genres_list='', years_list='', amount_from='', amount_to='', author=''):
        if title != '':
            self.query = self.query.filter(Book.title.ilike(f'%{title}%'))
        if '0' not in years_list and years_list != []:
            years_list = [int(x) for x in years_list]
            self.query = self.query.filter(Book.year.in_(years_list))
        if amount_from != '':
            self.query = self.query.filter(Book.amount >= int(amount_from))
        if amount_to != '':
            self.query = self.query.filter(Book.amount <= int(amount_to))
        if author != '':
            self.query = self.query.filter(Book.author.ilike(f'%{author}%'))
        return self.query.order_by(Book.year.desc())

class ImageSaver:
    def __init__(self, file):
        self.file = file

    def save(self):
        self.img = self.__find_by_md5_hash()
        if self.img is not None:
            return self.__find_by_md5_hash().id
        file_name = secure_filename(self.file.filename)
        last_id = Cover.query.order_by(Cover.id.desc()).first()
        if last_id is None:
            last_id = 0
        else: last_id = last_id.id
        self.img = Cover(
            id=last_id + 1,
            file_name=str(last_id + 1) + file_name,
            mime_type=self.file.mimetype,
            md5_hash=self.md5_hash)
        try:
            db.session.add(self.img)
            db.session.commit()
            self.file.save(
                os.path.join(app.config['UPLOAD_FOLDER'],
                            self.img.storage_filename))
        except:
            self.img.id = None
        return self.img.id

    def __find_by_md5_hash(self):
        self.md5_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return Cover.query.filter(Cover.md5_hash == self.md5_hash).first()