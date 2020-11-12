- [x] Customers can add themselves to the waitlist via SMS
	- [x] Build an Autopilot task to capture reservation information
	- [x] Create a card in the Trello waitlist
	- [x] Check if the customer is on the waitlist already

- [x] Customers can remove themselves from the waitlist
	- [x] Need an Autopilot task to be removed from the waitlist
	- [x] Create an endpoint in Flask to handle the customer request
		- [x] Is the customer in the waitlist?
		- [x] Determine where on the board the customer exists.
		- [x] Process confirmations properly
	- [x] Create a function in trello.py to move the card to the Cancellations list
	- [x] Remove the Sync Map entry

- [x] Customers can get their place on the waitlist
	- [x] Need an Autopilot task to get their location on waitlist
		- [x] Refine the samples for each task
	- [x] Get all the cards on the waitlist to determine position
	- [x] Handle when customer has a card on board, but not on the waitlist.
		- I.e. if they are on the "No Show" or "Table is Ready" lists they are told their table is ready.
- [x] Customers can get the length of the waitlist
	- [x] Follow-up would you like to join the waitlist?

- [x] Business can send text reminders when table is ready
	- [x] Click to send button for extra nudge
	- [x] Add labels to visually show when nudges are sent
	- [x] Track number of reminders sent
		- Use the card metadata for retrieving labels
	- [x] Trello API for adding labels to a card
	- [x] Create labels for table nudges
	- [x] Reference IDs of the labels in the card add label API
	- [x] Remove hardcoded label in table-is-ready
	- [x] Change name of the red label

- [x] Business should be able to view all the customer preferences

- [x] Create Twilio Sync map for mapping customer phone numbers to their cards on the board

- [x] Create Custom Fields to capture important customer attributes (especially attributes that could be utilized to send messages.)
  	- [x] Name
    - [x] Phone Number

- [x] When a card is archived remove the Sync entry
	- [x] Create a rule on Trello board when card is archived
	- [x] Create a Flask endpoint to delete Sync entry for the archived card
	- [x] Send phone number as a part of the archive action to the endpoint

- [] Allow staff to create a new card for walk-in customers
	- [x] Create new entry in Sync
	- [x] Collect information about the customer
	- [x] Click to send confirmation for phone number
	- [x] Setup a Twilio Studio Flow to help make this happen
	- [x] Track activities in the Trello card comments
	- [x] Send custom parameters to the Studio Flow
	- [x] Add an unverified label to the card
		- [x] Create label for "unverified"
		- [x] Add label when "confirm phone" is clicked
		- [] Remove label once phone is verified
			- [] Create a Trello function to remove labels
	- [x] Handle Twilio Studio Flow to handle where a customer doesn't confirm their phone number.
		- [x] Send a second confirmation text
		- [x] Create a label on the card to alert the business the phone number hasn't been verified.

- [x] Track customer interactions in the card comments
	- [x] When did the customer join the waitlist
	- [x] When was their table ready.
	- [x] When were reminders sent.
	- [x] When did the customer cancel their table.

- [] Setup all one-time Trello assets with a single method.
	- [x] Create lists on our Trello board
	- [x] Create our Trello labels
	- [x] Create custom fields on the card
	- [] Create card buttons
	- [] Create board rules

- [] Setup Twilio assets in deploy()
	- [] Create the Studio Flow
	- [] Add check to make sure Flow doesn't already exist.
	- [] Deploy Autopilot bot
	- [] Create Sync Service



- [] Update the get_trello_card_id to return the raw ID.
- [] Create function to retrieve Trello IDs using the API instead of hardcoding as variables.
- [] Handle when customer asks where they are in line and provide custom messages depending where they are.
- [] Remove "Cancel" from the messenger opt-out keywords
- [] Handle default messages to the bot.  Change the assistant_initiation to something more meaningful.
- [] Look at deploying on Heroku



