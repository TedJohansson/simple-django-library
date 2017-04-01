# -*- coding: latin-1 -*-


from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.generic import View
from students.forms import StudentForm
from students.models import Students
from books.forms import GetStudentForm
from books.models import Books, Borrowship
from django.contrib import messages


def index(request):
    return HttpResponse("Vad fan du vill typ")

class ViewStudents(View):
    def get(self, request):
        return render(request, "index.html")

class AddStudent(View):
    FORM_CLASS = StudentForm

    MODEL = Students

    def get(self, request):
        form = self.FORM_CLASS()

        return render(request, "add_student.html", {"form": form})

    def post(self, request):
        form = self.FORM_CLASS(request.POST)

        if form.is_valid():
            new_student = self.MODEL(**form.cleaned_data)

            new_student.save()

            form = self.FORM_CLASS()

            return render(request, "add_student.html", {"form": form, "message": "Student tillagd"})

        return render(request, "add_student.html", {"form": form})

class StudentView(View):

    FORM_CLASS = GetStudentForm

    def get(self, request, pk, *args, **kwargs):
        students = Students.objects.all().order_by("lastname")
        form = self.FORM_CLASS()

        student = Students.objects.get(pk=pk)
        try:
            loans = Borrowship.objects.filter(student=Students(pk), returned=False)
            books = []
            for loan in loans:
                book = Books.objects.get(pk=loan.book.pk)
                books.append(book)
        except Borrowship.DoesNotExist:
            books = []

        return render(request, "student.html", {"students": students,
                                                "student": student,
                                                "books": books})

    def post(self, request, pk):
        students = Students.objects.all().order_by("lastname")
        student = Students.objects.get(pk=pk)
        book = request.POST.get('book')

        try:
            loan = Borrowship.objects.get(book=Books(book), student=Students(pk), returned=False)
            loan.returned = True
            book = Books.objects.get(pk=book)
            book.amount += 1
            book.save()
            loan.save()
            send_mail(
                'Skolbiblioteket',
                """Hej {0}:
Hoppas {1} va bra, tack f�r att du l�mnade tillbaka den s� andra elever kan l�sa den.

Glada h�lsningar

Skolbiblioteket""".format(student.firstname, book.title),
                'lilbiblan@skf.com',
                [student.email.replace("\n", ""), ],
                fail_silently=False,
            )


        except Borrowship.DoesNotExist:
            pass

        try:
            loans = Borrowship.objects.filter(student=Students(pk), returned=False)
            books = []
            for loan in loans:
                book = Books.objects.get(pk=loan.book.pk)
                books.append(book)
        except Borrowship.DoesNotExist:
            books = []

        return render(request, "student.html", {"students": students,
                                             "student": student,
                                             "books": books,})