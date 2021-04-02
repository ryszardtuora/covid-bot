import datetime
import time
import json
import re
import uuid


month_table = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]
week_table = ["poniedziałek", "wtorek", "środę", "czwartek", "piątek", "sobotę", "niedzielę"]
hour_table = ["pierwsz", "drug", "trzeci", "czwart", "piąt", "szóst", "siódm", "ósm", "dziewiąt", "dziesiąt", "jedenast", "dwunast", "trzynast", "czternast", "piętnast", "szesnast", "siedemnast", "osiemnast", "dziewiętnast", "dwudziest"]

YEAR = 2021
hour_regex = re.compile(r"(((pierwsz)|(drug)|(trzeci)|(czwart)|(piąt)|(szóst)|(siódm)|(ósm)|(dziewiąt)|(dziesiąt)|(jedenast)|(dwunast)|(trzynast)|(czternast)|(piętnast)|(szesnast)|(siedemnast)|(osiemnast)|(dziewiętnast)|(dwudziest))((a)|(ą)|(i?ej))( po południu)? ?){1,2}|([0-2]?[0-9]:[0-6][0-9])")
day_regex = re.compile(r"(jutro)|(pojutrze)|(dzi[(ś)(siaj)])|(poniedziałek|wtorek|środę|czwartek|piątek|sobotę|niedzielę)|( [1-3]?[0-9](ego)? )")
month_regex = re.compile(r"(stycznia)|(lutego)|(marca)|(kwietnia)|(maja)|(czerwca)|(lipca)|(sierpnia)|(września)|(października)|(listopada)|(grudnia)")
number_regex = re.compile(r"\d+")


def process_hour(hour_match, now):
	minutes = 0
	hour = 8
	if hour_match == None:
		return hour, minutes
	hour_string = hour_match.group(0)
	if number_regex.search(hour_string) is None:
		words = hour_string.split()
		hour = 0
		for w in words:
			for i, h in enumerate(hour_table):
				if w.startswith(h):
					hour += i + 1
	else:
		hour, minutes = hour_string.split(":")
		hour = int(hour)
		minutes = int(minutes)
	if "po południu" in hour_string:
		hour += 12
	if hour > 24:
		hour = 8
	if minutes > 59:
		minutes = 0

	return hour, minutes
		

def process_day(day_match, now):
	today = now.tm_mday
	if day_match == None:
		return today
	day_string = day_match.group(0)
	if day_string.startswith("dzi"):
		return today
	elif day_string == "jutro":
		return today + 1
	elif day_string == "pojutrze":		
		return today + 2
	elif day_string in week_table:
		weekday_number = week_table.index(day_string)+1
		week_delta = weekday_number - now.tm_wday
		if week_delta > 0 :
			return today + week_delta
		else:
			return today + (7 - week_delta)
	else:
		day_number = int(number_regex.search(day_string).group(0))
		if day_number > 0 and day_number <32:
			return day_number
		else:
			return today

def process_month(month_match, now):
	this_month = now.tm_mon
	if month_match == None:
		return this_month
	month_string = month_match.group(0)
	try:
		month_number = month_table.index(month_string) + 1
		return month_number
	except IndexError:
		return this_month

def analyze_timestring(timestring):
	timestring = timestring.lower()
	now = time.localtime()

	hour_match = hour_regex.search(timestring)
	hour, minutes = process_hour(hour_match, now)

	day_match = day_regex.search(timestring)
	day = process_day(day_match, now)

	month_match = month_regex.search(timestring)
	month = process_month(month_match, now)

	year = YEAR
	dt = datetime.datetime(year = year, month = month, day = day, hour = hour, minute = minutes)

	return dt

def add_meeting(person_name, meeting_time):
    with open("meetings.json") as f:
        meetings_data = json.load(f)
    new_id = str(uuid.uuid4())
    meeting = {"id": new_id, "person_name":person_name, "meeting_time":meeting_time}
    meetings_data.append(meeting)
    with open("meetings.json", "w") as f:
        json.dump(meetings_data, f)
