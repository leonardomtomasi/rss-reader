import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

# RSS url from Modern Campus Calendar
rss_url = "https://api.calendar.moderncampus.net/pubcalendar/cc36e5e8-4b78-48b7-aebf-27102640ef4d/rss?category=cb4bca04-cb7e-4b98-a6be-7fc69c61f382&category=e79c85e2-e378-4b9a-9206-b7af2c5e00fb&category=8405f58a-2af0-4a39-9978-bbb089146259&url=https%3A%2F%2Fwww.apu.edu%2Fcalendar%2Fcampus-events%2F&hash=true"

response = requests.get(rss_url)
if response.status_code != 200:
    print("Failed to fetch RSS feed:", response.status_code)
    exit()

# Parse the XML response
root = ET.fromstring(response.content)

# Define namespace for `cal:` elements
ns = {'cal': "https://moderncampus.com/Data/cal/"}

# Set California timezone (Pacific Time)
california_tz = pytz.timezone("America/Los_Angeles")

# Extract events
events = []
now = datetime.now(pytz.utc)

for item in root.findall(".//item"):
    title = item.find("title").text
    link = item.find("link").text
    description = item.find("description")
    description_text = description.text if description is not None else "No description available"
    
    # Clean up HTML tags using BeautifulSoup
    description_text = BeautifulSoup(description_text, "html.parser").get_text()

    start = item.find("cal:start", ns)

    if start is not None:
        # Convert to UTC datetime object first
        event_start = datetime.fromisoformat(start.text.rstrip("Z")).replace(tzinfo=pytz.utc)

        # Convert to California time zone
        event_start_california = event_start.astimezone(california_tz)

        # Filter future events
        if event_start_california >= now:
            events.append((event_start_california, title, description_text, link))

# Sort and display events
events.sort()
for event in events:
    print(f"--------------------------")
    print()
    print(f"{event[0].strftime('%Y-%m-%d %I:%M %p')}")
    print(f"Title: {event[1]}")
    print(f"Description: {event[2]}")
    print(f"Link: {event[3]}\n")
