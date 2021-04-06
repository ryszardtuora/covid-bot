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
    if r.status_code != 200:
        raise APIError(f'Covid data API response returned {r.status_code}.')
    content = json.loads(r.content)
    until_today_data = content[-1]
    until_yesterday_data = content[-2]
    today_stats = {
        'confirmed': until_today_data['Confirmed'] - until_yesterday_data['Confirmed'],
        'deaths': until_today_data['Deaths'] - until_yesterday_data['Deaths'],
        'recovered': until_today_data['Recovered'] - until_yesterday_data['Recovered'],
        'active': until_today_data['Active'] - until_yesterday_data['Active']
    }
    return today_stats


class APIError(Exception):
    pass
