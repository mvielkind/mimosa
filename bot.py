import trello
import json
import os
from twilio.rest import Client
from flask import Flask, request
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_SYNC_SERVICE = 'IS64c852fe6f8101aacfa6be27bc7823ca'
TWILIO_SYNC_MAP = 'MP0ccdd2257c7a41e7a3fa39b3f728e850'


@app.route("/confirm-waitlist-join", methods=["POST"])
def confirm_waitlist_join():
	"""
	Confirms if the customer wants to join the waitlist.
	"""
	memory = json.loads(request.values["Memory"])
	confirm = memory["twilio"]["collected_data"]["confirm_waitlist"]["answers"]["confirm"]["answer"]

	if confirm == "Yes":
		next_action = [
			{
				"redirect": "task://add_to_waitlist"
			}
		]
	else:
		next_action = [
			{
				"say": "No problem! You can ask to join the waitlist at any time!"
			}
		]

	return {
		"actions": next_action
	}



@app.route("/number-in-line", methods=["POST"])
def number_in_line():
	"""
	Get the number of people currently on the waitlist.
	"""
	memory = json.loads(request.values["Memory"])
	phone_number = memory["twilio"]["sms"]["From"]
	phone_number = "+15555555555"

	# Get all cards in list.
	cards = trello.get_cards_in_list("Waitlist")

	# Is the current customer already in line?
	card = trello.get_trello_card_id(phone_number)
	# TODO: Handle when customer has a card on board, but not on the waitlist.
	if card:
		card_id = card.data["trello_card_id"]

		# Turn this into a function to get place in line.
		for i, c in enumerate(cards):
			if card_id == c["id"]:
				break

		next_action = [
			{
				"say": f"There are {str(i)} people in front of you on the wait list."
			}
		]
	else:
		next_action = [
			{
				"say": f"There are {len(cards)} people on the wait list right now."
			},
			{
				"redirect": "task://ask_join_waitlist"
			}
		]
		


	return {
		"actions": next_action
	}


@app.route("/add-to-waitlist", methods=["POST"])
def add_to_waitlist():
	# Parse the bot response to get the customer information.
	memory = json.loads(request.values["Memory"])
	phone_number = memory["twilio"]["sms"]["From"]
	phone_number = "+15555555555"

	# TODO: Perform a check to see if customer is already on the waitlist.
	if trello.check_if_card_exists(phone_number):
		return {
			"actions": [
				{
					"say": "Looks like you're already on the waitlist."
				}
			]
		}

	customer_answers = memory["twilio"]["collected_data"]["customer_info"]["answers"]

	# Create card title with name and party size.
	customer_name = customer_answers["customer_name"]["answer"]
	party_size = customer_answers["party_size"]["answer"]
	title = f"{customer_name}: {party_size}"

	# Detailed information.
	desc = "\n".join([f"{q.replace('_', ' ').title()}: {a['answer']}" for q, a in customer_answers.items()])
	desc = "\n".join([desc, f"Phone Number: {phone_number}"])

	# Trigger creating a card in Trello.
	card = trello.create_card_in_waitlist(title, desc, phone_number)
	card_id = json.loads(card.text)["id"]

	# Update the custom fields on the card.
	response = trello.update_custom_fields(card_id, "name", customer_name)
	print(response)
	response = trello.update_custom_fields(card_id, "phone_number", phone_number)

	return {
		"actions": [
			{
				"say": "Added to waitlist."
			}
		]
	}


@app.route("/remove-from-waitlist", methods=["POST"])
def remove_from_waitlist():
	memory = json.loads(request.values["Memory"])
	phone_number = memory["twilio"]["sms"]["From"]
	phone_number = "+15555555555"

	# Is there a card for the customer?
	if not trello.check_if_card_exists(phone_number):
		return {
			"actions": [
				{
					"say": "We can't find you on the wait list. If you would like to be added you can ask me to 'join the waitlist'"
				}
			]
		}

	# Handle Confirm "No" v. "Yes".
	customer_answers = memory["twilio"]["collected_data"]["waitlist_remove"]["answers"]
	confirm_answer = customer_answers["confirm"]["answer"]

	if confirm_answer.lower() == "no":
		return {
			"actions": [
				{
					"say": "Grand! We will see you soon!"
				}
			]
		}
	else:
		card = trello.get_trello_card_id(phone_number)
		card_id = card.data["trello_card_id"]
		response = trello.update_card_list(card_id, "Cancellations")
		removed = trello.remove_customer_from_sync_map(phone_number)

	return {
		"actions": [
			{
				"say": "You have been removed from the wait list."
			}
		]
	}



@app.route("/table-is-ready", methods=["POST"])
def table_is_ready():
	dat = json.loads(request.data)

	customer_name = dat["name"]
	to_number = dat["phone_number"]
	to_number = TWILIO_TO_NUMBER

	msg = f"Howdy {customer_name}! Your table is ready, make your way back to the restaurant so we can get you seated."

	twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	response = twilio_client.messages.create(
		body=msg,
		from_=TWILIO_FROM_NUMBER,
		to=to_number
	)

	return "SUCCESS"


if __name__ == "__main__":
	app.run()
