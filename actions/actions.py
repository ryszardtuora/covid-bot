# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import spacy
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction

from contact_utils import extract_name, add_contact, get_closest_contact
from api_utils import get_currency_rates, get_todays_covid_data, APIError
from time_utils import analyze_timestring, add_meeting
from qa_utils import get_matching_questions, get_answer

nlp = spacy.load("pl_spacy_model_morfeusz")

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
        top_3_questions = get_matching_questions(question)
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


class ActionSubmitContactForm(Action):

    def name(self) -> Text:
        return "action_submit_contact_form"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_name = tracker.get_slot("person")
        email = tracker.get_slot("email")
        name = extract_name(slot_name, nlp)
        data = {"name": name, "email": email}
        add_contact(data)
        confirmation_message = "Dodano kontakt {} o emailu {}".format(name, email)
        dispatcher.utter_message(confirmation_message)
        return [SlotSet("person", name), SlotSet("email", email)]


class ActionSubmitMeetingForm(Action):

    def name(self) -> Text:
        return "action_submit_meeting_form"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("person")
        contact = get_closest_contact(name)
        contact_name = contact["name"]
        time = tracker.get_slot("time")
        meeting_time = str(analyze_timestring(time))
        add_meeting(contact_name, meeting_time)
        confirmation_message = "Dodano spotkanie z {} na datę {}".format(name, meeting_time)
        dispatcher.utter_message(confirmation_message)
        return [SlotSet("person", contact_name), SlotSet("time", meeting_time)]


class ActionGetForex(Action):

    def name(self) -> Text:
        return "action_get_forex"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        rates = get_currency_rates()
        dispatcher.utter_message(text=rates)
        return []


class ActionRecoverContactEmail(Action):

    def name(self) -> Text:
        return "action_recover_contact_email"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("person")
        contact = get_closest_contact(name)
        contact_name = contact["name"]
        contact_email = contact["email"]
        message = "Mail {} to {}".format(contact_name, contact_email)
        dispatcher.utter_message(message)
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

