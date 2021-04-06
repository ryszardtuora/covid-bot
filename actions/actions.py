# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import spacy
import json
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction

from api_utils import get_todays_covid_data, APIError

from qa_utils import get_matching_questions, get_answer

from datetime import datetime

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Hello World!")
        return []


class ActionMatchQuestion(Action):

    def name(self) -> Text:
        return "action_match_question"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        question = tracker.latest_message["text"]
        top_3 = get_matching_questions(question)
        top_3_questions = [q[0] for q in top_3]
        least_distance = top_3[0][1]
        if least_distance > 0.4:
            dispatcher.utter_message("Nie udało mi się zrozumieć Twojego pytania, proszę spróbuj je sformułować inaczej.")
            return []
        top_3_answers = [get_answer(q) for q in top_3_questions]
        top_3_questions_string = "\ta) {}\n\tb) {}\n\tc) {}".format(*top_3_questions)
        questions_message = "Wybierz o które z pytań Ci chodziło:\n\n{}\n\nWpisz a), b) lub c)".format(top_3_questions_string)
        dispatcher.utter_message(questions_message)
        answers_for_slot = "<SEP>".join(top_3_answers)
        return [SlotSet("QA", answers_for_slot)]


class ActionAnswerQuestion(Action):

    def name(self) -> Text:
        return "action_answer_question"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        choice = tracker.latest_message["text"].strip()
        answers = tracker.get_slot("QA").split("<SEP>")
        print(answers)
        if choice in ["a", "a)"]:
            index = 0
        elif choice in ["b", "b)"]:
            index = 1
        elif choice in ["c", "c)"]:
            index = 2
        answer = answers[index]
        dispatcher.utter_message(answer)
        return []


class ActionSubmitSurveyForm(Action):

    def name(self) -> Text:
        return "action_submit_survey_form"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        survey_slots = ["survey_age", "survey_sex", "survey_education", "survey_location", "survey_household", "survey_remote", "survey_vaccine", "survey_infection", "survey_economy"]
        survey_data = {}
        for slot in survey_slots:
            value = tracker.get_slot(slot)
            survey_data[slot] = value
        survey_data["date"] = str(datetime.utcnow())
        with open("surveys.json") as f:
            surveys = json.load(f)
        surveys.append(survey_data)
        with open("surveys.json", "w") as f:
            json.dump(surveys, f, indent=2)
        return []


class ActionCheckCovidData(Action):

    def name(self) -> Text:
        return "action_check_covid_data"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            covid_data = get_todays_covid_data()
            message = self._prepare_message(covid_data)
        except APIError:
            message = 'Nie udało się uzyskać danych dotyczących COVID-19. Przepraszamy!'
        dispatcher.utter_message(message)
        return []

    def _prepare_message(self, covid_data: dict):
        message = f'Dzisiaj odnotowano {covid_data["confirmed"]} nowych przypadków zakażeń koronawirusem.\n'
        message += f'Liczba osób uznanych za wyzdrowiałe wynosi {covid_data["recovered"]}, '
        message += f'a zmarłych {covid_data["deaths"]}.\n'
        if covid_data['active'] == 0:
            message += 'Liczba osób aktywnie zakażonych COVID-19 nie zmieniła się od wczoraj.'
        else:
            active_difference = "zwiększyła się o" if covid_data["active"] > 0 else "zmniejszyła się o"
            active_difference_number = abs(covid_data['active'])
            message += f'Od wczoraj, liczba osób aktywnie zakażonych {active_difference} {active_difference_number}.'
        return message

