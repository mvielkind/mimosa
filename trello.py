import os
import requests
from dotenv import load_dotenv
load_dotenv()


TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD = "5f7312a009963d58f67798cd"


def create_card_in_waitlist():
	"""
	Create a new customer card in the waitlist.
	"""
	url = "https://api.trello.com/1/cards"

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'idList': "test",
		'name': 'Created with Python'
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)

	print(response.text)


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

	print(response.text)
