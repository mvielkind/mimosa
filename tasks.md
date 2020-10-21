- [x] Customers can add themselves to the waitlist via SMS
	- [x] Build an Autopilot task to capture reservation information
	- [x] Create a card in the Trello waitlist
	- [] Check if the customer is on the waitlist already

- [] Customers can remove themselves from the waitlist
	- [x] Need an Autopilot task to be removed from the waitlist
	- [] Create an endpoint in Flask to handle the customer request
		- [] Is the customer in the waitlist?
		- [] Determine where on the board the customer exists.
		- [] Process confirmations properly
	- [] Create a function in trello.py to move the card to the Cancellations list
	- [] Remove the Sync Map entry

- [x] Customers can get their place on the waitlist
	- [] Need an Autopilot task to get their location on waitlist
		- [] Refine the samples for each task
	- [x] Get all the cards on the waitlist to determine position
	- [] Handle when customer has a card on board, but not on the waitlist.
- [x] Customers can get the length of the waitlist
	- [x] Follow-up would you like to join the waitlist?

- [] Business can click button to send relevant alerts
	- [] Your table is ready
	- [] Reply to confirm your phone number

- [] Business can send text reminders when table is ready
	- [] Click to send button for extra nudge
	- [] Add labels to visually show when nudges are sent

- [x] Business should be able to view all the customer preferences

- [x] Create Twilio Sync map for mapping customer phone numbers to their cards on the board

- [x] Create Custom Fields to capture important customer attributes (especially attributes that could be utilized to send messages.)
  	- [x] Name
    - [x] Phone Number

- [] When a card is archived remove the Sync entry
	- [] Create a rule on Trello board when card is archived
	- [] Create a Flask endpoint to delete Sync entry for the archived card
	- [] Send phone number as a part of the archive action to the endpoint

- [] Allow staff to create a new card for walk-in customers
	- [] Create new entry in Sync
	- [] Collect information about the customer
	- [] Click to send confirmation for phone number

