import datetime
import re
import calendar

# Sample data structure for room prices
room_prices = {
    "Classic Deluxe": {
        "low_season": 800,
        "mid_season": 900,
        "high_season": 950
    },
    "Deluxe": {
        "low_season": 800,
        "mid_season": 900,
        "high_season": 950
    },
    "Superior": {
        "low_season": 750,
        "mid_season": 800,
        "high_season": 850
    },
    "G-House": {
        "low_season": 750,
        "mid_season": 800,
        "high_season": 850
    }
}

# Sample data structure for seasons
seasons = {
    (2, 22): "low_season",
    (3, 15): "mid_season",
    (3, 29): "high_season",
    (5, 17): "mid_season",
    (5, 24): "low_season", 
}

def parse_date(date_string):
    if isinstance(date_string, datetime.date):
        return date_string
    
    date_patterns = [
        r'(\d{1,2})[-.\s](\d{1,2}|[A-Za-z]+)[-.\s](\d{4})',  # DD-MM-YYYY, DD.MM.YYYY, DD Month YYYY
        r'(\d{4})[-.\s](\d{1,2}|[A-Za-z]+)[-.\s](\d{1,2})',  # YYYY-MM-DD, YYYY.MM.DD, YYYY Month DD
        r'([A-Za-z]+)\s(\d{1,2})[-,.\s]+(\d{4})'             # Month DD, YYYY
    ]
    
    for pattern in date_patterns:
        match = re.match(pattern, date_string)
        if match:
            groups = match.groups()
            if len(groups[0]) == 4:  # YYYY-MM-DD format
                year, month, day = groups
            elif groups[0].isalpha():  # Month DD, YYYY format
                month, day, year = groups
            else:  # DD-MM-YYYY format
                day, month, year = groups
            
            # Convert month name to number if it's a string
            if isinstance(month, str) and not month.isdigit():
                try:
                    month = list(calendar.month_abbr).index(month[:3].title())
                except ValueError:
                    try:
                        month = list(calendar.month_name).index(month.title())
                    except ValueError:
                        raise ValueError(f"Invalid month name: {month}")
            
            return datetime.date(int(year), int(month), int(day))
    
    raise ValueError("Invalid date format. Please use DD-MM-YYYY, DD.MM.YYYY, YYYY-MM-DD, YYYY.MM.DD, or Month DD, YYYY.")

def get_season(date):
    for season_start, season_name in sorted(seasons.items(), reverse=True):
        if (date.month, date.day) >= season_start:
            return season_name
    return "low_season"  # Default to low season if no match found

def get_price(room_type, date):
    season = get_season(date)
    return room_prices[room_type][season]

def extract_info_from_text(text):
    room_types = "|".join(room_prices.keys())
    room_pattern = re.compile(f"({room_types})", re.IGNORECASE)
    date_pattern = re.compile(r'\b(\d{1,2}[-./]\d{1,2}[-./]\d{4}|\d{4}[-./]\d{1,2}[-./]\d{1,2}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b', re.IGNORECASE)

    room_match = room_pattern.search(text)
    date_match = date_pattern.search(text)

    room_type = room_match.group(1) if room_match else None
    date = date_match.group(1) if date_match else None

    return room_type, date

def generate_response(text):
    room_type, date = extract_info_from_text(text)
    
    response = "Thank you for your inquiry. Here's the information you requested:\n\n"

    if date:
        try:
            date = parse_date(date)
        except ValueError as e:
            return str(e)

    if room_type and date:
        price = get_price(room_type, date)
        response += f"The price for a {room_type} room on {date.strftime('%B %d, %Y')} is ${price} per night."
    elif room_type:
        response += f"Prices for {room_type} room:\n"
        for season in ["low_season", "mid_season", "high_season"]:
            response += f"- {season.replace('_', ' ').title()}: ${room_prices[room_type][season]} per night\n"
    elif date:
        response += f"Prices for {date.strftime('%B %d, %Y')}:\n"
        for room in room_prices:
            price = get_price(room, date)
            response += f"- {room}: ${price} per night\n"
    else:
        response += "Our room types and price ranges:\n"
        for room in room_prices:
            min_price = min(room_prices[room].values())
            max_price = max(room_prices[room].values())
            response += f"- {room}: ${min_price} - ${max_price} per night\n"

    return response

# Example usage
print(generate_response("I'd like to book a Classic Deluxe room for July 15, 2024"))
print("\n" + "="*50 + "\n")
print(generate_response("What are the rates for a Deluxe room?"))
print("\n" + "="*50 + "\n")
print(generate_response("I'm planning a trip on March 15, 2024. What are the room rates?"))
print("\n" + "="*50 + "\n")
print(generate_response("Can you give me information about your room types and prices?"))
print("\n" + "="*50 + "\n")
print(generate_response("I'm interested in the G-House for December 25, 2024"))