import os
import json
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
load_dotenv()


TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD = "5f7312a009963d58f67798cd"
TRELLO_WAITLIST_ID = "5f731c76dcdc6e64abcd472f"
TRELLO_LISTS = {
	"Waitlist": "5f731c76dcdc6e64abcd472f",
	"Cancellations": "5f731cbcfeff7640ed977775",
	"No Show": "5f731c83bb3c235228212c4f"
}
TRELLO_FIELDS = {
	"name": "5f75c09969ea425523bfc858",
	"phone_number": "5f75c0993f480350c397b27f"
}
TRELLO_NUDGE_LABELS = {
	1: "5f901e37af41b47d964966da",
	2: "5f901eaba2bffd0ffdc671a2",
	3: "5f901eb8e8a97923cba5a94c"
}

TRELLO_LABELS = {
	"Unverified": "5f7312a0cdabcf46c0e3f57e"
}

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SYNC_SERVICE = 'IS64c852fe6f8101aacfa6be27bc7823ca'
TWILIO_SYNC_MAP = 'MP0ccdd2257c7a41e7a3fa39b3f728e850'


def get_list_id(list_name):
	"""
	Get the ID of the list name provided.
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

	all_lists = json.loads(response.text)
	for l in all_lists:
		if l["name"] == list_name:
			return l["id"]

	return None


def get_label_id(label_name):
	url = f"https://api.trello.com/1/boards/{TRELLO_BOARD}/labels"

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN
	}

	response = requests.request(
	   "GET",
	   url,
	   params=query
	)

	all_labels = json.loads(response.text)
	for l in all_labels:
		if l["name"] == label_name:
			return l["id"]

	return None


def get_field_id(field_name):
	url = f"https://api.trello.com/1/boards/{TRELLO_BOARD}/customFields"

	headers = {
	   "Accept": "application/json"
	}

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN
	}

	response = requests.request(
	   "GET",
	   url,
	   headers=headers,
	   params=query
	)

	all_fields = json.loads(response.text)
	for l in all_fields:
		if l["name"] == field_name:
			return l["id"]

	return None


def get_nudge_label(n_nudge):
	return TRELLO_NUDGE_LABELS[n_nudge]


def add_label_to_card(card_id, label_id):
	"""
	Adds a label to a card.
	"""
	url = f"https://api.trello.com/1/cards/{card_id}/idLabels"

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN,
	   'value': label_id
	}

	response = requests.request(
	   "POST",
	   url,
	   params=query
	)

	return response
	

def check_if_card_exists(phone_number):
	"""
	"""
	card_id = get_trello_card_id(phone_number)

	if card_id:
		return True
	else:
		return False


def get_trello_card_id(phone_number):
	"""
	Gets the Trello Card ID for a phone number.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	try:
		response = client.sync \
			.services(TWILIO_SYNC_SERVICE) \
			.sync_maps(TWILIO_SYNC_MAP) \
			.sync_map_items(phone_number) \
			.fetch()
	except TwilioRestException:
		return None

	return response


def get_card(card_id):
	"""
	Get a specific Trello card.
	"""
	url = f"https://api.trello.com/1/cards/{card_id}"

	headers = {
	   "Accept": "application/json"
	}

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN
	}

	response = requests.request(
	   "GET",
	   url,
	   headers=headers,
	   params=query
	)

	return json.dumps(json.loads(response.text))


def remove_customer_from_sync_map(phone_number):
	"""
	Removes the Sync Map item for the customer.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	sync_map_item = client.sync \
		.services(TWILIO_SYNC_SERVICE) \
		.sync_maps(TWILIO_SYNC_MAP) \
		.sync_map_items(phone_number) \
		.delete()

	return sync_map_item


def get_cards_in_list(trello_list):
	"""
	Return all the cards for a specific Trello list.
	"""
	try:
		list_id = get_list_id(trello_list)
		assert list_id
	except AssertionError:
		msg = f"Could not find list: {trello_list}."
		raise AssertionError(msg)

	url = f"https://api.trello.com/1/lists/{list_id}/cards"

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


def add_customer_to_sync_map(phone_number, card_id):
	"""
	Adds a new customer entry to the Sync Map.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	# Check if phone number exists in map.
	try:
		sync_map_item = client.sync \
			.services(TWILIO_SYNC_SERVICE) \
			.sync_maps(TWILIO_SYNC_MAP) \
			.sync_map_items \
			.create(key=phone_number, data={
				"trello_card_id": card_id
			})
	except TwilioRestException:
		sync_map_item = client.sync \
			.services(TWILIO_SYNC_SERVICE) \
			.sync_maps(TWILIO_SYNC_MAP) \
			.sync_map_items(phone_number) \
			.update(data={"trello_card_id": card_id})

	return sync_map_item


def create_card_in_waitlist(title, desc, phone_number):
	"""
	Create a new customer card in the waitlist.
	"""
	url = "https://api.trello.com/1/cards"

	trello_waitlist_id = get_list_id("Waitlist")

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'idList': trello_waitlist_id,
		'name': title,
		'desc': desc
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)

	card_id = json.loads(response.text)["id"]

	# Create the Sync Map entry for phone number.
	sync_item = add_customer_to_sync_map(phone_number, card_id)

	return response


def update_card_description(card_id, desc):
	url = f"https://api.trello.com/1/cards/{card_id}"

	headers = {
	   "Accept": "application/json"
	}

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN,
	   'desc': desc
	}

	response = requests.request(
	   "PUT",
	   url,
	   headers=headers,
	   params=query
	)

	return response


def update_card_list(card_id, new_list):
	"""
	Assign a card to a new list.
	"""
	url = f"https://api.trello.com/1/cards/{card_id}"

	headers = {
	   "Accept": "application/json"
	}

	try:
		new_list_id = get_list_id(new_list)
		assert new_list_id
	except AssertionError:
		msg = f"Could not find list: {new_list}"
		raise AssertionError(msg)

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN,
	   'idList': new_list_id
	}

	response = requests.request(
	   "PUT",
	   url,
	   headers=headers,
	   json=query
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


def add_card_comment(card_id, comment_text):
	url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN,
	   'text': comment_text
	}

	response = requests.request(
	   "POST",
	   url,
	   params=query
	)


def update_custom_fields(card_id, field_name, value):
	try:
		custom_field_id = get_field_id(field_name)
		assert custom_field_id
	except AssertionError:
		msg = f"Could not find field name: {field_name}"
		raise AssertionError(msg)

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


