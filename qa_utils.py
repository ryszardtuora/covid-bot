import json
from sklearn.metrics.pairwise import cosine_distances
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

with open("QA.json") as f:
  QA = json.load(f)

with open("QVEX.json") as f:
  QVEX = json.load(f)


questions = list(QA.keys())
answers = list(QA.values())
vex = list(QVEX.values())

def get_matching_questions(sent):
  vec = model.encode(sent)
  dists = cosine_distances([vec], vex)[0]
  ranking = sorted([(v,i) for i,v in enumerate(dists)])
  top_3 = [questions[e[1]] for e in ranking[:3]]
  return top_3

def get_answer(question):
  return QA[question]


