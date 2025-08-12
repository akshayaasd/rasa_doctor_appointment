from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pymongo import MongoClient
import os
import dateparser
from datetime import datetime, time as dt_time

class ActionSaveAppointmentToDB(Action):
    def name(self) -> Text:
        return "action_save_appointment_to_db"

    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(mongo_uri)
        self.db = self.client["Doctor_app"]
        self.collection = self.db["schedules"]

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name = tracker.get_slot("name") or "Unknown"
        phone_number = tracker.get_slot("phone_number") or "Unknown"
        specialization = tracker.get_slot("specialization") or "doctor"
        raw_date = tracker.get_slot("date") or "unknown date"
        raw_time = tracker.get_slot("time") or "unknown time"

        parsed_date = dateparser.parse(raw_date)
        if parsed_date:
            date_str = parsed_date.strftime("%Y-%m-%d")
        else:
            date_str = raw_date

        parsed_time = dateparser.parse(raw_time)
        if parsed_time:
            time_obj = parsed_time.time()
            if dt_time(10, 0) <= time_obj <= dt_time(22, 0):
                time_str = time_obj.strftime("%I:%M %p")
            else:
                dispatcher.utter_message(text="Please provide a time between 10 AM and 10 PM.")
                return []
        else:
            dispatcher.utter_message(text="I couldn't understand the time you provided. Please specify a time between 10 AM and 10 PM.")
            return []

        appointment_data = {
            "name": name,
            "phone_number": phone_number,
            "specialization": specialization,
            "date": date_str,
            "time": time_str
        }

        self.collection.insert_one(appointment_data)

        dispatcher.utter_message(
            text=f"Your appointment with the {specialization} is booked for {date_str} at {time_str}. See you then!"
        )

        return []
