from django.shortcuts import render


def home(request):
    products = [
        {
            "name": "Focus Desk Kit",
            "category": "Productivity Gear",
            "metric": "$129",
            "note": "Desk mat, cable hub, timer cube, laptop riser, and magnetic notes for a cleaner work setup",
        },
        {
            "name": "Commute Command Kit",
            "category": "Car Accessories",
            "metric": "$89",
            "note": "MagSafe mount, seat-gap organizer, fast charger, microfiber pouch, and emergency utility light",
        },
        {
            "name": "Executive Reset Bundle",
            "category": "Hybrid Bundle",
            "metric": "$199",
            "note": "A premium workday bundle for the desk, bag, and car built around focus and readiness",
        },
    ]
    return render(request, "showcase/home.html", {"products": products})
