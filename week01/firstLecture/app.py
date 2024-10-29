from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.exceptions import NotFound

app = Flask(__name__)
api = Api(app)


class BookModel:
    def __init__(self, pk, title, author):
        self.pk = pk
        self.title = title
        self.author = author

    def __str__(self):
        return f"{self.pk} Book title: {self.title} from {self.author}"

    def to_dict(self):
        return {"pk": self.pk, "title": self.title, "author": self.author}


books = [
    BookModel(num, f"Title {num}", f"Author {num}")
    for num in range(1, 6)
]


class BooksResource(Resource):
    def get(self):
        return [b.to_dict() for b in books]

    def post(self):
        pk = books[-1].pk
        pk += 1
        data = request.get_json()
        book = BookModel(pk, **data)
        books.append(book)
        return book.to_dict()


class BookResource(Resource):
    def get(self, pk):
        try:
            book = [b for b in books if b.pk == pk][0]
            return book.to_dict()
        except IndexError:
            raise NotFound()

    def put(self, pk):
        data = request.get_json()
        try:
            book = [b for b in books if b.pk == pk][0]
            book.title = data['title']
            return book.to_dict()
        except IndexError:
            return {"message": "Book not found"}, 404

    def delete(self, pk):
        try:
            book = [b for b in books if b.pk == pk][0]
            books.remove(book)
            return 204
        except IndexError:
            return {"message": "Book not found"}, 404


api.add_resource(BooksResource, "/books")
api.add_resource(BookResource, "/books/<int:pk>")
