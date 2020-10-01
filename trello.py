import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()


TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD = "5f7312a009963d58f67798cd"
TRELLO_WAITLIST_ID = "5f731c76dcdc6e64abcd472f"
TRELLO_FIELDS = {
	"name": "5f75c09969ea425523bfc858",
	"phone_number": "5f75c0993f480350c397b27f"
}


def create_card_in_waitlist(title, desc):
	"""
	Create a new customer card in the waitlist.
	"""
	url = "https://api.trello.com/1/cards"

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'idList': TRELLO_WAITLIST_ID,
		'name': title,
		'desc': desc
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)

	return response


def get_lists_on_board():
	"""
	Get all the of the lists on a board.
	"""
	url = f"https://api.trello.com/1/boards/{TRELLO_BOARD}/lists"

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN
	}

	response = requests.request(
		"GET",
		url,
		params=query
	)

	return response.text


def update_custom_fields(card_id, field_name, value):
	custom_field_id = TRELLO_FIELDS[field_name]
	url = f"https://api.trello.com/1/cards/{card_id}/customField/{custom_field_id}/item"

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN,
	   'modelType': 'card',
	   'value': {
	   		'text': value
	   }
	}

	response = requests.request(
	   "PUT",
	   url,
	   json=query
	)

	return response


def create_custom_fields():
	"""
	"""
	url = "https://api.trello.com/1/customFields"

	headers = {
	   "Accept": "application/json"
	}

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN,
	   'idModel': TRELLO_BOARD,
	   'modelType': 'board',
	   'type': 'text',
	   'pos': 1,
	   'display_cardFront': 'false'
	}

	for f in ["name", "phone_number"]:
		query["name"] = f

		response = requests.request(
		   "POST",
		   url,
		   headers=headers,
		   params=query
		)

		print(json.loads(response.text))
