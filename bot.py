import trello
import json
import os
from twilio.rest import Client 
from flask import Flask, request

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCONUT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER")


@app.route("/remove-from-waitlist", methods=["POST"])
def remove_from_waitlist():
	memory = json.loads(request.values["Memory"])
	phone_number = memory["twilio"]["sms"]["From"]

	# Mask the phone number for demo.
	phone_number = "+15555555"

	print(memory["twilio"]["collected_data"])

	# Get the card associated with the phone number.

	# Check if card exists in the waitlist.

	# If yes, move card to the cancellation list.

	return {
		"actions": [
			{"say": "You've been removed from the list."}
		]
	}



@app.route("/add-to-waitlist", methods=["POST"])
def add_to_waitlist():
	memory = json.loads(request.values["Memory"])
	phone_number = memory["twilio"]["sms"]["From"]

	# Mask phone number for demo.
	phone_number = "+15555555"

	# Check if there is a card associated with the phone number already.
	if trello.get_customer_card_id(phone_number):
		return {
			"actions": [
				{"say": "Looks like you're already on the waitlist!"}
			]
		}

	customer_answers = memory["twilio"]["collected_data"]["customer_info"]["answers"]

	customer_name = customer_answers["customer_name"]["answer"]
	party_size = customer_answers["party_size"]["answer"]

	# Build the card title that will be the customer name and party size.
	title = f"{customer_name}: {party_size}"

	# Build the card description from the customer answers.
	description = "\n".join([f"{q.replace('_', ' ').title()}: {a['answer']}" for q, a in customer_answers.items()])
	description = "\n".join([description, f"Phone Number: {phone_number}"])

	# Trigger creating a card in Trello.
	card = trello.create_card_in_waitlist(title, description, phone_number)
	card_id = json.loads(card.text)["id"]
	print(card_id)

	# Add a quick attachement.
	trello.add_attachment_to_card(card_id)

	# Update custom fields for the card.
	response = trello.update_card_custom_fields(card_id, "name", customer_name)
	print(response.text)
	response = trello.update_card_custom_fields(card_id, "phone_number", phone_number)
	print(response.text)

	return {
		"actions": [
			{"say": "Added to waitlist."}
		]
	}


@app.route("/table-is-ready", methods=["POST"])
def table_is_ready():
	dat = json.loads(request.data)

	to_number = dat["phone_number"]
	# Mask the phone number for now.
	to_number = TWILIO_TO_NUMBER
	msg = f"Howdy {dat['name']}! Your table is ready!"

	twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	response = twilio_client.messages.create(
		body=msg,
		from_=TWILIO_FROM_NUMBER,
		to=to_number
	)

	return {"STATUS": 200}


if __name__ == "__main__":
	app.run()
