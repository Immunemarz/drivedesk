from django.shortcuts import render


PRODUCTS = [
    {
        "name": "DriveDesk Tech Pouch",
        "category": "Carry",
        "price": "$58",
        "tagline": "The hero pouch for cables, charger, pen, cloth, and daily carry tools.",
        "details": "Structured pouch with elastic loops, zip mesh, microfiber sleeve, and compact desk-to-car carry.",
        "image_url": "https://images.pexels.com/photos/9185853/pexels-photo-9185853.jpeg?cs=srgb&dl=pexels-timur-weber-9185853.jpg&fm=jpg",
    },
    {
        "name": "Executive Carry Case",
        "category": "Carry",
        "price": "$74",
        "tagline": "A larger organizer for charger bricks, adapters, notebook, and small tools.",
        "details": "Dual-layer hard-shell case with cord channels, pen sleeve, passport pocket, and grab loop.",
        "image_url": "https://images.pexels.com/photos/34929061/pexels-photo-34929061.jpeg?cs=srgb&dl=pexels-a-a-54155102-34929061.jpg&fm=jpg",
    },
    {
        "name": "Desk Reset Rail",
        "category": "Desk",
        "price": "$34",
        "tagline": "Hide the visual noise under your workstation.",
        "details": "Under-desk cable tray with magnetic clips, soft ties, and edge anchors for a cleaner surface.",
        "image_url": "https://images.pexels.com/photos/34934741/pexels-photo-34934741.jpeg?cs=srgb&dl=pexels-a-a-54155102-34934741.jpg&fm=jpg",
    },
    {
        "name": "Aluminum Laptop Riser",
        "category": "Desk",
        "price": "$49",
        "tagline": "Better posture without making your desk look busy.",
        "details": "Low-profile riser with cable pass-through, non-slip base, and minimal brushed finish.",
        "image_url": "https://images.pexels.com/photos/13279384/pexels-photo-13279384.jpeg?cs=srgb&dl=pexels-pramodtiwari-13279384.jpg&fm=jpg",
    },
    {
        "name": "Commute Command Pouch",
        "category": "Car",
        "price": "$89",
        "tagline": "A cleaner glovebox and console pouch for the daily driver.",
        "details": "Vehicle pouch with charger, cloth, registration sleeve, pen, tire gauge, and emergency light.",
        "image_url": "https://images.pexels.com/photos/30563035/pexels-photo-30563035.jpeg?cs=srgb&dl=pexels-andreas-naslund-92380530-30563035.jpg&fm=jpg",
    },
    {
        "name": "MagSafe Dash Mount",
        "category": "Car",
        "price": "$39",
        "tagline": "Secure phone placement that still looks premium.",
        "details": "Strong magnetic mount with low-glare angle control and woven USB-C cable.",
        "image_url": "https://images.pexels.com/photos/4824425/pexels-photo-4824425.jpeg?cs=srgb&dl=pexels-maksgelatin-4824425.jpg&fm=jpg",
    },
    {
        "name": "Seat-Gap Organizer",
        "category": "Car",
        "price": "$29",
        "tagline": "A simple fix for keys, cards, receipts, and cables.",
        "details": "Slim organizer with card sleeve, cable notch, and soft-touch interior.",
        "image_url": "https://images.pexels.com/photos/6969025/pexels-photo-6969025.jpeg?cs=srgb&dl=pexels-lynxexotics-6969025.jpg&fm=jpg",
    },
    {
        "name": "Full Reset Bundle",
        "category": "Bundles",
        "price": "$168",
        "tagline": "The best carry, desk, and car pieces in one daily system.",
        "details": "DriveDesk Tech Pouch, Desk Reset Rail, MagSafe Dash Mount, and microfiber pouch bundled together.",
        "image_url": "https://images.pexels.com/photos/30868621/pexels-photo-30868621.jpeg?cs=srgb&dl=pexels-efrem-efre-2786187-30868621.jpg&fm=jpg",
    },
    {
        "name": "Creator Transit Bundle",
        "category": "Bundles",
        "price": "$212",
        "tagline": "A larger premium bundle for people moving between desk, studio, and car.",
        "details": "Executive Carry Case, Aluminum Laptop Riser, Commute Command Pouch, and cable essentials.",
        "image_url": "https://images.pexels.com/photos/34929061/pexels-photo-34929061.jpeg?cs=srgb&dl=pexels-a-a-54155102-34929061.jpg&fm=jpg",
    },
]


def home(request):
    featured_products = [
        {
            "name": product["name"],
            "category": product["category"],
            "metric": product["price"],
            "note": product["tagline"],
            "image_url": product["image_url"],
        }
        for product in (PRODUCTS[0], PRODUCTS[4], PRODUCTS[6])
    ]
    return render(request, "showcase/home.html", {"products": featured_products})


def products(request):
    categories = ["All", "Desk", "Car", "Carry", "Bundles"]
    return render(
        request,
        "showcase/products.html",
        {"products": PRODUCTS, "categories": categories},
    )
