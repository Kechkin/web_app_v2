from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime

# database
currency_db = {}



class Node:
    def __init__(self, data, course):
        self.left = None
        self.right = None
        self.data = data
        self.course = course

    def insert(self, data, course):
        if self.data:
            if data < self.data:
                if self.left is None:
                    self.left = Node(data, course)
                else:
                    self.left.insert(data, course)

            elif data > self.data:
                if self.right is None:
                    self.right = Node(data, course)
                else:
                    self.right.insert(data, course)
        else:
            self.data = data

    def find(self, value, last=None):
        if value < self.data:
            if self.left is None:
                if last:
                    return last
                else:
                    return {self.data: self.course}
            return self.left.find(value, last)

        elif value > self.data:
            last = {self.data: self.course}
            if self.right is None:
                return last
            return self.right.find(value, last)
        else:
            return {self.data: self.course}


# check number
def is_number(n):
    try:
        if float(n) > 0:
            return True
    except ValueError:
        return False


# decorators
def add_decor(func):
    def wrapped(request):
        if request.POST["currency"].isalpha() and is_number(request.POST["course"]):
            return func(request)
        else:
            return HttpResponse("Введите верные данные")

    return wrapped


def convert_decor(func):
    def wrapped(request):
        if request.method == "POST":
            if is_number(request.POST['money']):
                return func(request)
            else:
                return HttpResponse("Введите верные данные")
        else:
            return func(request)

    return wrapped


# main part
def index(request):
    context = {
        "currency_db": currency_db
    }
    return render(request, 'app_convert_v2/index.html', context)


def search(request):
    if request.method == "POST":
        if request.POST['currency'] in currency_db:
            result = currency_db[request.POST['currency']].find(request.POST['time'])
            context = {
                "currency": request.POST['currency'],
                "data": result,
                "currency_db": currency_db
            }
        else:
            return HttpResponse("There is no currency in DB")
        return render(request, 'app_convert_v2/search.html', context)


@add_decor
def add_data(request):
    if request.method == "POST":
        current_time = datetime.now().strftime("%d.%m.%y %H:%M")
        if request.POST['currency'] in currency_db:
            currency_db[request.POST['currency']].insert(current_time, request.POST['course'])
        else:
            currency_db[request.POST['currency']] = Node(current_time, request.POST['course'])
    return render(request, 'app_convert_v2/add_data.html')


@convert_decor
def converter_to(request):
    if request.method == "POST":
        context = {
            "money": request.POST['money'],
            "time": request.POST['time'],
            "time2": request.POST['time2'],
            "currency": request.POST['currency'],
            "currency2": request.POST['currency2'],
            "currency_db": currency_db
        }
        if not context["time"] and ["time2"]:
            current_time = datetime.now().strftime("%d.%m.%y %H:%M")
            context["time"], context["time2"] = current_time, current_time
        value1 = currency_db[request.POST['currency']].find(request.POST['time'])
        value2 = currency_db[request.POST['currency2']].find(request.POST['time2'])
        result = "%.2f" % ((float(context["money"]) * float(*value1.values())) / float(*value2.values()))
        context2 = {
            "time": context["time"],
            "time2": context["time2"],
            "currency": request.POST['currency'],
            "currency2": request.POST['currency2'],
            "result": result
        }
        return render(request, 'app_convert_v2/convert_result.html', context2)

    elif request.method == "GET":
        context2 = {
            "currency_db": currency_db
        }
        return render(request, 'app_convert_v2/converter_to.html', context2)
