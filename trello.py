import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()


TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD = os.getenv("TRELLO_BOARD_ID")
TRELLO_WAITLIST_ID = os.getenv("TRELLO_WAITLIST_ID")

TRELLO_FIELDS = {
	"name": os.getenv("TRELLO_FIELD_NAME"),
	"phone_number": os.getenv("TRELLO_FIELD_NUMBER")
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


def update_card_custom_fields(card_id, field_name, value):
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


def get_lists_on_board():
	"""
	Get all the of the lists on a board.

	returns: a list of all the lists that are included on the board.
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

	return json.loads(response.text)


def add_attachment_to_card(card_id):
	url = f"https://api.trello.com/1/cards/{card_id}/attachments"

	headers = {
 	  "Accept": "application/json"
	}

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'url': "https://www.theyoungfolks.com/wp-content/uploads/2016/06/Marlin-and-Nemo.jpg"
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)


def create_custom_fields():
	"""
	Add custom fields to the board for customer name and phone number.

	Having these custom fields will allow Trello to use these fields in the messages that are sent.
	"""
	url = "https://api.trello.com/1/customFields"

	headers = {
		"Accept": "application/json"
	}

	base_query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'idModel': TRELLO_BOARD,
		'modelType': 'board',
		'type': 'text',
		'pos': 1,
		'display_cardFront': "false"
	}

	for f in ["name", "phone_number"]:
		base_query["name"] = f

		response = requests.request(
			"POST",
			url,
			headers=headers,
			params=base_query
		)

		print(json.loads(response.text))
