"""Mock data layer for SkyWay Airlines AI Agent."""
import random, string
from datetime import datetime, timedelta

# ── Airports ──────────────────────────────────────────────────────────────────
AIRPORTS = {
    "JFK": {"name": "John F. Kennedy International", "city": "New York", "country": "USA", "timezone": "UTC-5"},
    "LAX": {"name": "Los Angeles International",     "city": "Los Angeles", "country": "USA", "timezone": "UTC-8"},
    "LHR": {"name": "Heathrow",                      "city": "London", "country": "UK",  "timezone": "UTC+0"},
    "DXB": {"name": "Dubai International",           "city": "Dubai", "country": "UAE", "timezone": "UTC+4"},
    "SIN": {"name": "Changi",                        "city": "Singapore", "country": "SGP","timezone": "UTC+8"},
    "CDG": {"name": "Charles de Gaulle",             "city": "Paris", "country": "France","timezone": "UTC+1"},
    "HND": {"name": "Haneda",                        "city": "Tokyo", "country": "Japan","timezone": "UTC+9"},
    "SYD": {"name": "Kingsford Smith",               "city": "Sydney", "country": "AUS", "timezone": "UTC+11"},
    "ORD": {"name": "O'Hare International",          "city": "Chicago", "country": "USA","timezone": "UTC-6"},
    "BOM": {"name": "Chhatrapati Shivaji Maharaj",   "city": "Mumbai", "country": "India","timezone": "UTC+5:30"},
    "DEL": {"name": "Indira Gandhi International",   "city": "Delhi", "country": "India","timezone": "UTC+5:30"},
}

# ── Flights ───────────────────────────────────────────────────────────────────
FLIGHTS = [
    {"id":"SW101","airline":"SkyWay","from":"JFK","to":"LAX","dep":"08:00","arr":"11:30","dur":"5h 30m","stops":0,"eco":249,"biz":749,"first":1299},
    {"id":"SW202","airline":"SkyWay","from":"JFK","to":"LHR","dep":"22:00","arr":"10:00+1","dur":"7h 00m","stops":0,"eco":599,"biz":1499,"first":2899},
    {"id":"SW303","airline":"SkyWay","from":"LAX","to":"DXB","dep":"14:00","arr":"20:00+1","dur":"16h 00m","stops":1,"eco":799,"biz":2199,"first":3999},
    {"id":"SW404","airline":"SkyWay","from":"LHR","to":"SIN","dep":"09:30","arr":"05:30+1","dur":"13h 00m","stops":0,"eco":699,"biz":1899,"first":3299},
    {"id":"SW505","airline":"SkyWay","from":"DXB","to":"HND","dep":"02:00","arr":"16:00","dur":"9h 00m","stops":0,"eco":549,"biz":1399,"first":2599},
    {"id":"SW606","airline":"SkyWay","from":"CDG","to":"JFK","dep":"11:00","arr":"13:30","dur":"8h 30m","stops":0,"eco":629,"biz":1599,"first":2999},
    {"id":"SW707","airline":"SkyWay","from":"SYD","to":"LAX","dep":"15:00","arr":"12:00","dur":"14h 00m","stops":0,"eco":879,"biz":2299,"first":4199},
    {"id":"SW808","airline":"SkyWay","from":"ORD","to":"LHR","dep":"17:30","arr":"07:30+1","dur":"8h 00m","stops":0,"eco":579,"biz":1449,"first":2699},
    {"id":"SW909","airline":"SkyWay","from":"BOM","to":"DXB","dep":"06:00","arr":"08:30","dur":"2h 30m","stops":0,"eco":199,"biz":549,"first":999},
    {"id":"SW110","airline":"SkyWay","from":"DEL","to":"LHR","dep":"02:30","arr":"07:30","dur":"9h 00m","stops":0,"eco":649,"biz":1699,"first":3199},
]

STATUS_POOL = ["On Time", "On Time", "On Time", "Delayed 15 mins", "Delayed 30 mins", "Boarding", "Departed", "Landed"]
GATE_POOL   = ["A12","B7","C3","D15","E2","A22","B19","C11"]

# ── In-memory bookings store ──────────────────────────────────────────────────
_bookings: dict = {
    "SWAB1234": {
        "pnr": "SWAB1234",
        "flight_id": "SW101",
        "airline": "SkyWay",
        "passenger": "Elite Traveler",
        "email": "elite@skyway.ai",
        "from": "JFK",
        "to": "LAX",
        "departure": "08:00",
        "arrival": "11:30",
        "class": "First",
        "seats": 1,
        "total_price": "$1299",
        "status": "Confirmed",
        "booked_at": "2025-05-01 12:00",
    }
}

def _pnr():
    return "SW" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def search_flights(origin: str, destination: str, date: str, travel_class: str = "economy") -> dict:
    origin      = origin.upper().strip()
    destination = destination.upper().strip()
    if origin not in AIRPORTS:
        return {"error": f"Unknown airport code '{origin}'. Supported: {', '.join(AIRPORTS)}"}
    if destination not in AIRPORTS:
        return {"error": f"Unknown airport code '{destination}'. Supported: {', '.join(AIRPORTS)}"}
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        if dt.date() < datetime.now().date():
            return {"error": "Travel date cannot be in the past."}
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD (e.g. 2025-08-20)."}
    cls = travel_class.lower()
    cls_map = {"economy":"eco","business":"biz","first":"first","first class":"first"}
    if cls not in cls_map:
        return {"error": f"Unknown class '{travel_class}'. Choose economy, business, or first."}
    price_key = cls_map[cls]
    results = [f for f in FLIGHTS if f["from"]==origin and f["to"]==destination]
    if not results:
        return {"flights": [], "message": f"No direct flights found from {origin} to {destination}. Try different airports."}
    formatted = []
    for f in results:
        price = f[price_key]
        formatted.append({
            "flight_id": f["id"],
            "airline": f["airline"],
            "from": f"{origin} ({AIRPORTS[origin]['city']})",
            "to": f"{destination} ({AIRPORTS[destination]['city']})",
            "departure": f"{f['dep']} on {date}",
            "arrival": f["arr"],
            "duration": f["dur"],
            "stops": "Non-stop" if f["stops"]==0 else f"{f['stops']} stop",
            "class": travel_class.title(),
            "price": f"${price}",
            "seats_available": random.randint(3, 42),
        })
    return {"flights": formatted, "count": len(formatted), "date": date}


def book_flight(flight_id: str, passenger_name: str, email: str,
                travel_class: str = "economy", seats: int = 1) -> dict:
    flight_id = flight_id.upper().strip()
    flight = next((f for f in FLIGHTS if f["id"] == flight_id), None)
    if not flight:
        return {"error": f"Flight '{flight_id}' not found. Use search_flights to find valid flight IDs."}
    if seats < 1 or seats > 9:
        return {"error": "Number of seats must be between 1 and 9."}
    if "@" not in email or "." not in email:
        return {"error": "Invalid email address format."}
    cls_map = {"economy":"eco","business":"biz","first":"first","first class":"first"}
    cls = travel_class.lower()
    if cls not in cls_map:
        return {"error": f"Unknown class '{travel_class}'."}
    base_price = flight[cls_map[cls]]
    total = base_price * seats
    pnr = _pnr()
    booking = {
        "pnr": pnr,
        "flight_id": flight_id,
        "airline": flight["airline"],
        "passenger": passenger_name,
        "email": email,
        "from": flight["from"],
        "to": flight["to"],
        "departure": flight["dep"],
        "arrival": flight["arr"],
        "class": travel_class.title(),
        "seats": seats,
        "total_price": f"${total}",
        "status": "Confirmed",
        "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _bookings[pnr] = booking
    return {"success": True, "booking": booking}


def get_booking(pnr: str) -> dict:
    pnr = pnr.upper().strip()
    if pnr not in _bookings:
        return {"error": f"No booking found with PNR '{pnr}'. Please check and try again."}
    return {"booking": _bookings[pnr]}


def cancel_booking(pnr: str) -> dict:
    pnr = pnr.upper().strip()
    if pnr not in _bookings:
        return {"error": f"No booking found with PNR '{pnr}'."}
    b = _bookings[pnr]
    if b["status"] == "Cancelled":
        return {"error": "This booking is already cancelled."}
    price_val = int(b["total_price"].replace("$","").replace(",",""))
    refund = int(price_val * 0.85)
    _bookings[pnr]["status"] = "Cancelled"
    return {"success": True, "pnr": pnr, "refund": f"${refund}", "message": f"Booking {pnr} cancelled. Refund of ${refund} (85%) will be credited in 5-7 business days."}


def get_flight_status(flight_id: str) -> dict:
    flight_id = flight_id.upper().strip()
    flight = next((f for f in FLIGHTS if f["id"] == flight_id), None)
    if not flight:
        return {"error": f"Flight '{flight_id}' not found."}
    status = random.choice(STATUS_POOL)
    gate   = random.choice(GATE_POOL)
    return {
        "flight_id": flight_id,
        "airline": flight["airline"],
        "route": f"{flight['from']} → {flight['to']}",
        "scheduled_dep": flight["dep"],
        "scheduled_arr": flight["arr"],
        "status": status,
        "gate": gate,
        "terminal": random.choice(["T1","T2","T3"]),
        "last_updated": datetime.now().strftime("%H:%M"),
    }


def list_airports() -> dict:
    result = []
    for code, info in AIRPORTS.items():
        result.append({"code": code, "name": info["name"], "city": info["city"], "country": info["country"], "timezone": info["timezone"]})
    return {"airports": result, "count": len(result)}


def get_baggage_policy(travel_class: str = "economy", airline: str = "SkyWay") -> dict:
    policies = {
        "economy": {"cabin": "1 bag up to 7kg", "checked": "1 bag up to 23kg", "extra_fee": "$60 per extra bag", "overweight_fee": "$100 per bag over 23kg"},
        "business": {"cabin": "2 bags up to 7kg each", "checked": "2 bags up to 32kg each", "extra_fee": "$80 per extra bag", "overweight_fee": "No overweight fee"},
        "first":    {"cabin": "2 bags up to 10kg each","checked": "3 bags up to 32kg each", "extra_fee": "No extra fee (up to 5 bags)", "overweight_fee": "No overweight fee"},
    }
    cls = travel_class.lower().replace("first class","first")
    if cls not in policies:
        return {"error": f"Unknown class '{travel_class}'."}
    return {"airline": airline, "class": travel_class.title(), "policy": policies[cls]}


def calculate_fare(flight_id: str, travel_class: str = "economy", seats: int = 1) -> dict:
    flight_id = flight_id.upper().strip()
    flight = next((f for f in FLIGHTS if f["id"] == flight_id), None)
    if not flight:
        return {"error": f"Flight '{flight_id}' not found."}
    cls_map = {"economy":"eco","business":"biz","first":"first","first class":"first"}
    cls = travel_class.lower()
    if cls not in cls_map:
        return {"error": f"Unknown class '{travel_class}'."}
    base = flight[cls_map[cls]]
    tax  = round(base * 0.12, 2)
    fuel = round(base * 0.08, 2)
    total_per = base + tax + fuel
    return {
        "flight_id": flight_id,
        "class": travel_class.title(),
        "seats": seats,
        "base_fare": f"${base}",
        "taxes": f"${tax}",
        "fuel_surcharge": f"${fuel}",
        "total_per_seat": f"${total_per}",
        "grand_total": f"${round(total_per * seats, 2)}",
    }
