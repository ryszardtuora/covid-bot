import requests
import json
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer


QA = {}
questions = []

# scraping danych
r = requests.get("https://www.gov.pl/web/koronawirus/pytania-i-odpowiedzi")
soup = BeautifulSoup(r.content, "html.parser")
pairs = soup.findAll("details")


# przetwarzanie pobranych danych
for p in pairs:
  question = p.find("summary").text
  questions.append(question)
  answer_children = list(p.children)[1:]
  answer_parts = []
  for ac in answer_children:
    try:
      answer_parts.append(ac.text)
    except AttributeError:
      pass
  answer = "\n".join(answer_parts)
  QA[question] = answer

# zapis par pytanie -> odpowiedź
with open("QA.json", "w") as f:
  json.dump(QA, f)


# wektoryzacja pytań
model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

QVEX = {}
for q in questions:
  QVEX[q] = model.encode(q).tolist()

with open("QVEX.json", "w") as f:
  json.dump(QVEX, f)


