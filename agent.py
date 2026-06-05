"""LLM agent with Gemini function calling for SkyWay Airlines."""
import json, os
from data import (
    search_flights, book_flight, get_booking,
    cancel_booking, get_flight_status, list_airports,
    get_baggage_policy, calculate_fare,
)

try:
    import google.genai as genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        USE_LEGACY = True
    except ImportError:
        GEMINI_AVAILABLE = False
        USE_LEGACY = False
else:
    USE_LEGACY = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

TOOLS_MAP = {
    "search_flights":    search_flights,
    "book_flight":       book_flight,
    "get_booking":       get_booking,
    "cancel_booking":    cancel_booking,
    "get_flight_status": get_flight_status,
    "list_airports":     list_airports,
    "get_baggage_policy":get_baggage_policy,
    "calculate_fare":    calculate_fare,
}

TOOL_DEFINITIONS = [
    {
        "name": "search_flights",
        "description": "Search available flights between two airports for a given date and travel class.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin":       {"type": "string", "description": "IATA origin airport code (e.g. JFK)"},
                "destination":  {"type": "string", "description": "IATA destination airport code (e.g. LAX)"},
                "date":         {"type": "string", "description": "Travel date in YYYY-MM-DD format"},
                "travel_class": {"type": "string", "description": "Class: economy, business, or first"},
            },
            "required": ["origin", "destination", "date"],
        },
    },
    {
        "name": "book_flight",
        "description": "Book a flight and create a reservation with passenger details.",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_id":      {"type": "string", "description": "Flight ID from search results (e.g. SW101)"},
                "passenger_name": {"type": "string", "description": "Full passenger name"},
                "email":          {"type": "string", "description": "Passenger email address"},
                "travel_class":   {"type": "string", "description": "Class: economy, business, or first"},
                "seats":          {"type": "integer","description": "Number of seats (1-9)"},
            },
            "required": ["flight_id", "passenger_name", "email"],
        },
    },
    {
        "name": "get_booking",
        "description": "Retrieve an existing booking by PNR (booking reference code).",
        "parameters": {
            "type": "object",
            "properties": {
                "pnr": {"type": "string", "description": "Booking PNR/reference code (e.g. SWAB12)"},
            },
            "required": ["pnr"],
        },
    },
    {
        "name": "cancel_booking",
        "description": "Cancel an existing booking and calculate refund.",
        "parameters": {
            "type": "object",
            "properties": {
                "pnr": {"type": "string", "description": "Booking PNR to cancel"},
            },
            "required": ["pnr"],
        },
    },
    {
        "name": "get_flight_status",
        "description": "Get real-time status for a flight by its flight ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_id": {"type": "string", "description": "Flight ID (e.g. SW101)"},
            },
            "required": ["flight_id"],
        },
    },
    {
        "name": "list_airports",
        "description": "List all supported airports with their codes, cities and countries.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_baggage_policy",
        "description": "Get baggage allowance policy for a travel class.",
        "parameters": {
            "type": "object",
            "properties": {
                "travel_class": {"type": "string", "description": "economy, business, or first"},
                "airline":      {"type": "string", "description": "Airline name"},
            },
            "required": ["travel_class"],
        },
    },
    {
        "name": "calculate_fare",
        "description": "Calculate total fare breakdown including taxes for a flight.",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_id":    {"type": "string", "description": "Flight ID (e.g. SW101)"},
                "travel_class": {"type": "string", "description": "economy, business, or first"},
                "seats":        {"type": "integer","description": "Number of seats"},
            },
            "required": ["flight_id"],
        },
    },
]

SYSTEM_PROMPT = """You are SkyBot, a friendly and knowledgeable AI assistant for SkyWay Airlines.
You help passengers with flight search, booking, cancellation, status checks, and travel information.

Guidelines:

- Always be warm, professional, and concise.
- Use the provided tools to fetch real data — never guess flight details.
- When presenting flight results, format them clearly with emojis.
- If the user provides incomplete info (e.g., missing date), ask for it politely.
- For bookings, always confirm details before proceeding.
- Provide currency in USD ($) format.
- Supported airports: JFK, LAX, LHR, DXB, SIN, CDG, HND, SYD, ORD, BOM, DEL.
- Always mention the PNR after a successful booking.
- IMPORTANT: When using tools, use ONLY the internal tool-calling mechanism. DO NOT write tags like <function> or [TOOL_CALL] in your text response.
"""

class AirlineAgent:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.groq_key   = os.getenv("GROQ_API_KEY", "")

        self.use_groq   = bool(self.groq_key) and GROQ_AVAILABLE
        self.use_gemini = bool(self.gemini_key) and GEMINI_AVAILABLE
        self.use_llm    = self.use_groq or self.use_gemini

        self.client_gemini = None
        self.client_groq   = None

        if self.use_groq:
            self.client_groq = Groq(api_key=self.groq_key)

        if self.use_gemini:
            if not USE_LEGACY:
                self.client_gemini = genai.Client(api_key=self.gemini_key)
            else:
                genai.configure(api_key=self.gemini_key)
                tools = [{"function_declarations": TOOL_DEFINITIONS}]
                self.model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=SYSTEM_PROMPT,
                    tools=tools,
                )

    def _call_tool(self, name: str, args: dict) -> str:
        fn = TOOLS_MAP.get(name)
        if not fn:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            result = fn(**args)
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _format_result(self, tool_name: str, result_str: str) -> str:
        """Format tool results into readable markdown."""
        try:
            data = json.loads(result_str)
        except Exception:
            return result_str

        if "error" in data:
            return f"❌ **Error:** {data['error']}"

        if tool_name == "search_flights":
            if not data.get("flights"):
                return f"✈️ {data.get('message', 'No flights found.')}"
            lines = [f"✈️ **{data['count']} flight(s) found for {data['date']}:**\n"]
            for f in data["flights"]:
                lines.append(
                    f"🔹 **{f['flight_id']}** — {f['from']} → {f['to']}\n"
                    f"   🕐 {f['departure']} → {f['arrival']}  |  ⏱ {f['duration']}  |  {f['stops']}\n"
                    f"   💺 {f['class']}  |  💰 {f['price']}  |  🪑 {f['seats_available']} seats left\n"
                )
            return "\n".join(lines)

        if tool_name == "book_flight":
            b = data.get("booking", {})
            return (
                f"✅ **Booking Confirmed!**\n\n"
                f"📋 **PNR:** `{b.get('pnr')}`\n"
                f"✈️ **Flight:** {b.get('flight_id')} — {b.get('from')} → {b.get('to')}\n"
                f"🕐 **Departure:** {b.get('departure')}  |  **Arrival:** {b.get('arrival')}\n"
                f"👤 **Passenger:** {b.get('passenger')}\n"
                f"💺 **Class:** {b.get('class')}  |  **Seats:** {b.get('seats')}\n"
                f"💰 **Total:** {b.get('total_price')}\n"
                f"📧 **Confirmation sent to:** {b.get('email')}\n\n"
                f"*Please save your PNR `{b.get('pnr')}` for future reference.*"
            )

        if tool_name == "get_booking":
            b = data.get("booking", {})
            status_icon = {"Confirmed": "✅", "Cancelled": "❌"}.get(b.get("status", ""), "ℹ️")
            return (
                f"{status_icon} **Booking Details — PNR `{b.get('pnr')}`**\n\n"
                f"✈️ **Flight:** {b.get('flight_id')} — {b.get('from')} → {b.get('to')}\n"
                f"🕐 **Departure:** {b.get('departure')}  |  **Arrival:** {b.get('arrival')}\n"
                f"👤 **Passenger:** {b.get('passenger')}\n"
                f"💺 **Class:** {b.get('class')}  |  **Seats:** {b.get('seats')}\n"
                f"💰 **Total:** {b.get('total_price')}\n"
                f"📊 **Status:** {b.get('status')}"
            )

        if tool_name == "cancel_booking":
            return (
                f"❌ **Booking Cancelled**\n\n"
                f"📋 **PNR:** `{data.get('pnr')}`\n"
                f"💵 **Refund:** {data.get('refund')}\n\n"
                f"{data.get('message', '')}"
            )

        if tool_name == "get_flight_status":
            st = data.get("status", "")
            icon = {"On Time": "🟢", "Boarding": "🟡", "Departed": "🔵", "Landed": "✅"}.get(st, "🟠")
            return (
                f"📡 **Flight Status — {data.get('flight_id')}**\n\n"
                f"✈️ **Route:** {data.get('route')}\n"
                f"🕐 **Scheduled:** {data.get('scheduled_dep')} → {data.get('scheduled_arr')}\n"
                f"{icon} **Status:** {st}\n"
                f"🚪 **Gate:** {data.get('gate')}  |  **Terminal:** {data.get('terminal')}\n"
                f"🕒 *Updated: {data.get('last_updated')}*"
            )

        if tool_name == "list_airports":
            lines = ["🌍 **Supported Airports:**\n"]
            for a in data.get("airports", []):
                lines.append(f"🔹 **{a['code']}** — {a['name']}, {a['city']}, {a['country']} ({a['timezone']})")
            return "\n".join(lines)

        if tool_name == "get_baggage_policy":
            p = data.get("policy", {})
            return (
                f"🧳 **Baggage Policy — {data.get('airline')} {data.get('class')}**\n\n"
                f"🎒 **Cabin:** {p.get('cabin')}\n"
                f"📦 **Checked:** {p.get('checked')}\n"
                f"💸 **Extra Bag Fee:** {p.get('extra_fee')}\n"
                f"⚖️ **Overweight Fee:** {p.get('overweight_fee')}"
            )

        if tool_name == "calculate_fare":
            return (
                f"💰 **Fare Breakdown — {data.get('flight_id')} ({data.get('class')})**\n\n"
                f"🧾 **Base Fare:** {data.get('base_fare')} × {data.get('seats')} seat(s)\n"
                f"🏛️ **Taxes:** {data.get('taxes')}\n"
                f"⛽ **Fuel Surcharge:** {data.get('fuel_surcharge')}\n"
                f"💵 **Per Seat Total:** {data.get('total_per_seat')}\n"
                f"✅ **Grand Total:** **{data.get('grand_total')}**"
            )

        return f"```json\n{result_str}\n```"

    def chat(self, user_message: str, history: list) -> str:
        """Process a user message and return AI response."""
        if self.use_groq:
            return self._groq_chat(user_message, history)
        if self.use_gemini:
            return self._gemini_chat(user_message, history)
        return self._demo_chat(user_message, history)

    def _groq_chat(self, user_message: str, history: list) -> str:
        """Use Groq (Llama-3) with function calling."""
        try:
            groq_tools = []
            for t in TOOL_DEFINITIONS:
                groq_tools.append({
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"]
                    }
                })

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for h in history:
                if h[0]: messages.append({"role": "user", "content": h[0]})
                if h[1]: messages.append({"role": "assistant", "content": h[1]})
            messages.append({"role": "user", "content": user_message})

            response = self.client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=groq_tools,
                tool_choice="auto",
                parallel_tool_calls=False
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    result_str    = self._call_tool(function_name, function_args)
                    formatted     = self._format_result(function_name, result_str)

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": result_str,
                    })

                second_response = self.client_groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages
                )
                final_text = second_response.choices[0].message.content
                return f"{formatted}\n\n---\n{final_text}"

            return response_message.content
        except Exception as e:
            return f"⚠️ **GROQ ERROR:** {str(e)}\n\n" + self._demo_chat(user_message, [])

    def _gemini_chat(self, user_message: str, history: list) -> str:
        """Use Gemini with function calling."""
        if self.client_gemini:  # new google.genai SDK
            return self._new_sdk_chat(user_message, history)
        # Legacy google.generativeai
        return self._legacy_sdk_chat(user_message, history)

    def _new_sdk_chat(self, user_message: str, history: list) -> str:
        """Use the new google.genai SDK."""
        try:
            tools = [genai_types.Tool(function_declarations=[
                genai_types.FunctionDeclaration(**{k: v for k, v in t.items()}) for t in TOOL_DEFINITIONS
            ])]
            contents = []
            for h in history:
                if h[0]: contents.append(genai_types.Content(role="user",  parts=[genai_types.Part(text=h[0])]))
                if h[1]: contents.append(genai_types.Content(role="model", parts=[genai_types.Part(text=h[1])]))
            contents.append(genai_types.Content(role="user", parts=[genai_types.Part(text=user_message)]))

            resp = self.client_gemini.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=tools,
                )
            )
            for _ in range(5):
                if resp.function_calls:
                    fc = resp.function_calls[0]
                    result_str = self._call_tool(fc.name, dict(fc.args))
                    formatted   = self._format_result(fc.name, result_str)
                    contents.append(resp.candidates[0].content)
                    contents.append(genai_types.Content(role="tool", parts=[
                        genai_types.Part(function_response=genai_types.FunctionResponse(
                            name=fc.name, response={"result": result_str}
                        ))
                    ]))
                    resp = self.client_gemini.models.generate_content(
                        model="gemini-2.0-flash", contents=contents,
                        config=genai_types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, tools=tools)
                    )
                    if resp.text:
                        return f"{formatted}\n\n---\n{resp.text}"
                    return formatted
                elif resp.text:
                    return resp.text
                break
            return "I couldn't process that. Please try again."
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                return (
                    "⚠️ **GRID CAPACITY EXCEEDED (429 ERROR)**\n\n"
                    "Your Gemini API key is currently being rate-limited by Google. This often happens with newly created keys or high traffic.\n\n"
                    "💡 **PRO TIP:** Wait 60 seconds or try again in a few minutes. In the meantime, I am switching to **SAFE MODE** to assist you with local records.\n\n"
                    "---\n" + self._demo_chat(user_message, [])
                )
            return f"⚠️ **NEURAL LINK ERROR:** {err_msg}\n\nFalling back to local protocols...\n\n" + self._demo_chat(user_message, [])

    def _legacy_sdk_chat(self, user_message: str, history: list) -> str:
        """Use legacy google.generativeai SDK."""
        try:
            msgs = []
            for h in history:
                if h[0]:
                    msgs.append({"role": "user", "parts": [h[0]]})
                if h[1]:
                    msgs.append({"role": "model", "parts": [h[1]]})

            chat_session = self.model.start_chat(history=msgs)
            response = chat_session.send_message(user_message)

            max_rounds = 5
            for _ in range(max_rounds):
                if not response.candidates:
                    break
                part = response.candidates[0].content.parts[0]
                if hasattr(part, "function_call") and part.function_call.name:
                    fc   = part.function_call
                    args = dict(fc.args)
                    result_str = self._call_tool(fc.name, args)
                    formatted  = self._format_result(fc.name, result_str)

                    response = chat_session.send_message(
                        genai.protos.Content(parts=[
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=fc.name,
                                    response={"result": result_str},
                                )
                            )
                        ], role="tool")
                    )
                    if response.candidates:
                        next_part = response.candidates[0].content.parts[0]
                        if hasattr(next_part, "text") and next_part.text:
                            return f"{formatted}\n\n---\n{next_part.text}"
                    return formatted
                elif hasattr(part, "text"):
                    return part.text
                break
            return "I'm sorry, I couldn't process that request. Please try again."
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                return (
                    "⚠️ **GRID CAPACITY EXCEEDED (429 ERROR)**\n\n"
                    "Your Gemini API key is currently being rate-limited by Google. This often happens with newly created keys.\n\n"
                    "💡 **PRO TIP:** Wait 60 seconds and try again. Switching to **SAFE MODE**...\n\n"
                    "---\n" + self._demo_chat(user_message, [])
                )
            return f"⚠️ **LLM error:** {err_msg}. Falling back to demo mode.\n\n" + self._demo_chat(user_message, [])

    def _demo_chat(self, user_message: str, history: list) -> str:
        """Rule-based demo mode when no API key is available."""
        msg = user_message.lower().strip()

        if any(w in msg for w in ["search", "find", "flight from", "fly from", "flights"]):
            import re
            codes = re.findall(r'\b([A-Z]{3})\b', user_message.upper())
            if len(codes) >= 2:
                result = search_flights(codes[0], codes[1], "2026-12-15", "economy")
                return self._format_result("search_flights", json.dumps(result))
            return ("✈️ I'd love to search flights for you! Please provide:\n"
                    "- **Origin airport code** (e.g., JFK)\n"
                    "- **Destination airport code** (e.g., LAX)\n"
                    "- **Travel date** (YYYY-MM-DD)\n"
                    "- **Class** (economy/business/first) *(optional)*")

        if any(w in msg for w in ["status", "track", "where is flight", "check flight"]):
            import re
            ids = re.findall(r'\bSW\d+\b', user_message.upper())
            if ids:
                result = get_flight_status(ids[0])
                return self._format_result("get_flight_status", json.dumps(result))
            return ("📡 To check flight status, please provide the **flight number** (e.g., SW101).\n"
                    "SkyWay flights are numbered SW101–SW909.")

        if any(w in msg for w in ["airport", "airports", "show airports", "list airports"]):
            result = list_airports()
            return self._format_result("list_airports", json.dumps(result))

        if any(w in msg for w in ["booking", "my booking", "pnr", "reservation"]):
            import re
            pnrs = re.findall(r'\bSW[A-Z0-9]{6}\b', user_message.upper())
            if pnrs:
                result = get_booking(pnrs[0])
                return self._format_result("get_booking", json.dumps(result))
            return ("📋 To retrieve your booking, please provide your **PNR** (e.g., SWAB1234).\n"
                    "Your PNR was sent to your email after booking.")

        if any(w in msg for w in ["baggage", "luggage", "bag allowance"]):
            cls = "business" if "business" in msg else ("first" if "first" in msg else "economy")
            result = get_baggage_policy(cls)
            return self._format_result("get_baggage_policy", json.dumps(result))

        if any(w in msg for w in ["cancel", "cancellation"]):
            import re
            pnrs = re.findall(r'\bSW[A-Z0-9]{6}\b', user_message.upper())
            if pnrs:
                result = cancel_booking(pnrs[0])
                return self._format_result("cancel_booking", json.dumps(result))
            return "To cancel a booking, please provide your **PNR** (e.g., SWAB1234)."

        if any(w in msg for w in ["fare", "price", "cost", "how much"]):
            import re
            ids = re.findall(r'\bSW\d+\b', user_message.upper())
            if ids:
                result = calculate_fare(ids[0])
                return self._format_result("calculate_fare", json.dumps(result))
            return "To calculate the fare, please provide a **flight ID** (e.g., SW101)."

        if any(w in msg for w in ["hello", "hi", "hey", "help", "start"]):
            return ("👋 Welcome to **SkyWay Airlines**! I'm SkyBot, your AI travel assistant.\n\n"
                    "Here's what I can help you with:\n"
                    "- ✈️ **Search Flights** — e.g., *Search JFK to LAX on 2026-12-20*\n"
                    "- 🎫 **Book a Flight** — e.g., *Book SW101 for John Doe*\n"
                    "- 📋 **View Booking** — e.g., *My booking SWAB1234*\n"
                    "- ❌ **Cancel Booking** — e.g., *Cancel booking SWAB1234*\n"
                    "- 📡 **Flight Status** — e.g., *Check flight SW101*\n"
                    "- 🌍 **Airports** — e.g., *Show airports*\n"
                    "- 🧳 **Baggage Policy** — e.g., *Baggage policy for business class*\n\n"
                    "How can I assist you today? 😊")

        return ("🤔 I didn't quite catch that. Here are some things you can ask me:\n\n"
                "- *\"Search flights from JFK to LHR on 2026-12-15\"*\n"
                "- *\"Check flight SW202\"*\n"
                "- *\"Show airports\"*\n"
                "- *\"Baggage policy for economy\"*\n\n"
                "💡 **Tip:** Add your Gemini API key in `.env` to enable full AI conversations!")
