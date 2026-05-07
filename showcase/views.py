from django.shortcuts import render


def home(request):
    products = [
        {
            "name": "Chrono Reserve",
            "category": "Swiss Watch",
            "metric": "$18.4K",
            "note": "Blue dial, 72-hour power reserve",
        },
        {
            "name": "Apex GT",
            "category": "Performance Coupe",
            "metric": "3.2s",
            "note": "0-60 acceleration with grand touring comfort",
        },
        {
            "name": "Capital OS",
            "category": "Productivity System",
            "metric": "+28%",
            "note": "Weekly output lift from sharper planning rituals",
        },
    ]
    return render(request, "showcase/home.html", {"products": products})
