from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_migrate import Migrate
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from werkzeug.exceptions import NotFound

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://postgres:test@localhost:5432/clothes'


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)
api = Api(app)
migrate = Migrate(app, db)


class BookModel(db.Model):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"<{self.id}> {self.title} from {self.author}"

    def as_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author}


class BooksResource(Resource):
    def get(self):
        books = db.session.execute(db.select(BookModel)).scalars()
        return [b.as_dict() for b in books]

    def post(self):
        data = request.get_json()
        new_book = BookModel(**data)
        db.session.add(new_book)
        db.session.commit()
        return new_book.as_dict(), 201


class BookResource(Resource):
    def get(self, id):
        try:
            book = db.session.execute(db.select(BookModel).filter_by(id=id)).scalar_one()
            return book.as_dict()
        except IndexError:
            raise NotFound()

    def put(self, id):
        data = request.get_json()
        try:
            book = db.session.execute(db.select(BookModel).filter_by(id=id)).scalar_one()
            book.title = data['title']
            db.session.commit()
            return {"message": f"Book with id {id} is updated."}
        except IndexError:
            return {"message": "Book not found"}, 404

    def delete(self, id):
        try:
            book = db.session.execute(db.select(BookModel).filter_by(id=id)).scalar_one()
            db.session.delete(book)
            db.session.commit()
            return {"message": f"Book with id {id} is deleted."}
        except IndexError:
            return {"message": "Book not found"}, 404


api.add_resource(BooksResource, '/books')
api.add_resource(BookResource, '/books/<int:id>')


if __name__ == '__main__':
    app.run(debug=True)
