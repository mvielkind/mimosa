import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


def create_sync_services():
	"""
	Create the Twilio Sync Service and the Sync Map to track customer phone numbers and the Trello card IDs.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	# Create the sync service.
	service = client.sync.services.create()
	service_id = service.sid

	# Create the Sync Map.
	sync_map = client.sync.services(service_id) \
		.sync_maps \
		.create()

	return service_id, sync_map.sid
