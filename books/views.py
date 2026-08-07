from rest_framework import viewsets
from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookListSerializer, BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer
