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


