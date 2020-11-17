import trello
import json
import os
import requests
from twilio.rest import Client
from flask import Flask, request
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_SYNC_SERVICE = 'IS64c852fe6f8101aacfa6be27bc7823ca'
TWILIO_SYNC_MAP = 'MP0ccdd2257c7a41e7a3fa39b3f728e850'
TWILIO_FLOW_SID = os.getenv("TWILIO_FLOW_SID")


@app.route("/remove-sync-map-entry", methods=["POST"])
def remove_sync_map_entry():
	"""
	Removes a phone number from the Sync Map.
	"""
	dat = json.loads(request.data)
	to_number = dat["phone_number"]

	output = trello.remove_customer_from_sync_map(to_number)

	return "SUCCESS"


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


@app.route("/has-preferences", methods=["POST"])
def has_preferences():
	memory = json.loads(request.values["Memory"])
	phone_number = memory["twilio"]["sms"]["From"]
	phone_number = "+15555555555"

	has_preference = memory["twilio"]["collected_data"]["customer_has_preferences"]["answers"]["ask_for_preferences"]["answer"]

	if has_preference == "No":
		return {
			"actions": [
				{
					"say": "You're on the waitlist!\n\nI'll send you a message when you're table is ready.\n\nAt anytime you can ask me 'where am I in line?' to see how many people are in front of you.\n\nSee you soon!"
				}
			]
		}

	return {
		"actions": [
			{
				"redirect": "task://get_preferences"
			}
		]
	}


@app.route("/process-preferences", methods=["POST"])
def process_preferences():
	memory = json.loads(request.values["Memory"])
	phone_number = memory["twilio"]["sms"]["From"]
	phone_number = "+15555555555"

	customer_preferences = memory["twilio"]["collected_data"]["collect_preferences"]["answers"]["customer_preferences"]["answer"]

	# Get the Trello card and build a new description.
	card = trello.get_trello_card_id(phone_number)
	card_id = card.data["trello_card_id"]
	card = json.loads(trello.get_card(card_id))
	print(card.keys())
	desc = card["desc"]

	preferences = f"Customer Preferences: {customer_preferences}."

	new_desc = "\n\n".join([desc, preferences])

	status = trello.update_card_description(card_id, new_desc)
	print(status)

	return {
		"actions": [
			{
				"say": "You're on the waitlist!\n\nI'll send you a message when you're table is ready.\n\nAt anytime you can ask me 'where am I in line?' to see how many people are in front of you.\n\nSee you soon!"
			}
		]
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
	response = trello.update_custom_fields(card_id, "phone_number", phone_number)

	# Add a comment on the card.
	response_comment = trello.add_card_comment(card_id, "Customer joined waitlist.")

	return {
		"actions": [
			{
				"redirect": "task://has_preferences"
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

		# Add a comment on the card.
		response_comment = trello.add_card_comment(card_id, "Customer cancelled.")

	return {
		"actions": [
			{
				"say": "You have been removed from the wait list."
			}
		]
	}


@app.route("/table-reminder", methods=["POST"])
def table_reminder():
	dat = json.loads(request.data)

	customer_name = dat["name"]
	to_number = dat["phone_number"]

	# Add new status label to card.
	card = trello.get_trello_card_id(dat["phone_number"])
	card_id = card.data["trello_card_id"]
	customer_card = json.loads(trello.get_card(card_id))
	card_labels = [l["color"] for l in customer_card["labels"] if l["color"] in ["green", "yellow", "red"]]
	label_n = len(card_labels) + 1
	if label_n > 3:
		label_n = 3

	if "red" in card_labels:
		nudge_label = "FinalNudge"
	elif "yellow" in card_labels:
		nudge_label = "FinalNudge"
	elif "green" in card_labels:
		nudge_label = "SecondNudge"
	else:
		nudge_label = "FirstNudge"

	nudge_id = trello.get_label_id(nudge_label)
	label_response = trello.add_label_to_card(card_id, nudge_id)

	# Add comment to track.
	response_comment = trello.add_card_comment(card_id, f"Customer reminder {str(label_n)} was sent.")

	# Send a more customized message to the customer.
	if label_n == 2:
		msg = f"Hi {customer_name} this is your second reminder your table is ready. Please make your way back to the restaurant to be seated."
	elif label_n == 3:
		msg = f"Hi {customer_name} this is your final reminder that your table is ready. Please make your way back to the restaurant to be seated."
	twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
	response = twilio_client.messages.create(
		body=msg,
		from_=TWILIO_FROM_NUMBER,
		to=to_number
	)

	# Handle moving card.
	if label_n == 3:
		response_move = trello.update_card_list(card_id, "No Show")

	return "SUCCESS"


@app.route("/table-is-ready", methods=["POST"])
def table_is_ready():
	dat = json.loads(request.data)

	customer_name = dat["name"]
	to_number = dat["phone_number"]

	# Send text message to customer alterting table is ready.
	msg = f"Howdy {customer_name}! Your table is ready, make your way back to the restaurant so we can get you seated."

	twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	response = twilio_client.messages.create(
		body=msg,
		from_=TWILIO_FROM_NUMBER,
		to=to_number
	)

	# Update label on card for first nudge.
	card = trello.get_trello_card_id(dat["phone_number"])
	card_id = card.data["trello_card_id"]
	nudge_label = trello.get_label_id("FirstNudge")
	trello.add_label_to_card(card_id, nudge_label)
	
	# Add a comment on the card.
	response_comment = trello.add_card_comment(card_id, "Table is ready for customer.")

	return "SUCCESS"


@app.route("/phone-unverified", methods=["POST"])
def phone_unverified():
	"""
	Triggered from Twilio Studio. Adds a label for an unverified phone number.
	"""
	card_id = request.values["card_id"]
	trello.add_label_to_card(card_id, "Unverified")

	return "SUCCESS"


@app.route("/confirm-phone", methods=["POST"])
def confirm_phone():
	dat = json.loads(request.data)
	customer_name = dat["name"]
	to_number = dat["phone_number"]
	card_id = dat["card_id"]

	# Create the Sync Map entry.
	map_item = trello.add_customer_to_sync_map(dat["phone_number"], card_id)

	# Call our Twilio Studio Flow to confirm phone number.
	twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
	response = twilio_client.studio.flows(TWILIO_FLOW_SID).executions.create(
		from_=TWILIO_FROM_NUMBER,
		to=to_number,
		parameters={
			'customer_name': customer_name,
			'card_id': card_id,
			'task': 'confirm-phone'
		}
	)

	# Log a comment to the card.
	comment_response = trello.add_card_comment(card_id, "Requested customer confirm phone number.")

	return "SUCCESS"


if __name__ == "__main__":
	app.run()
