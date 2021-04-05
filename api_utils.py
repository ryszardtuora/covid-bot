import json
import requests
import pandas

CURRENCIES = ["USD", "EUR", "GBP", "RUB", "JPY"]

def get_currency_rates():
	addr = r"https://api.exchangeratesapi.io/latest?base=PLN"
	r = requests.get(addr)
	content = json.loads(r.content)
	rates = [(k,1/content["rates"][k]) for k in CURRENCIES]
	df = pandas.DataFrame(rates)
	df.columns = ["Waluta", "Cena (w złotych)"]
	table = str(df)
	return table


def get_todays_covid_data():
    addr = 'https://api.covid19api.com/live/country/poland'
    r = requests.get(addr)
    content = json.loads(r.content)
    until_today_data = content[-1]
    until_yesterday_data = content[-2]
    today_stats = {
        'new_confirmed': until_today_data['Confirmed'] - until_yesterday_data['Confirmed'],
        'new_deaths': until_today_data['Deaths'] - until_yesterday_data['Deaths'],
        'new_recovered': until_today_data['Recovered'] - until_yesterday_data['Recovered'],
        'new_active': until_today_data['Active'] - until_yesterday_data['Active']
    }
    return today_stats
