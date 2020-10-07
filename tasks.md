- [x] Customers can add themselves to the waitlist via SMS
	- [x] Build an Autopilot task to capture reservation information
	- [x] Create a card in the Trello waitlist
	- [] Check if the customer is on the waitlist already

- [] Customers can remove themselves from the waitlist
	- [] Need an Autopilot task to be removed from the waitlist
	- [] Create an endpoint in Flask to handle the customer request
		- [] Is the customer in the waitlist?
		- [] Determine where on the board the customer exists.
		- [] Process confirmations properly
	- [] Create a function in trello.py to move the card to the Cancellations list
	- [] Remove the Sync Map entry

- [] Customers can get their place on the waitlist
	- [] Need an Autopilot task to get their location on waitlist
	- [] Get all the cards on the waitlist to determine position

- [] Business can click button to send relevant alerts
	- [] Your table is ready
	- [] Reply to confirm your phone number

- [] Business should be able to view all the customer preferences

- [] Create Twilio Sync map for mapping customer phone numbers to their cards on the board

- [] Create Custom Fields to capture important customer attributes (especially attributes that could be utilized to send messages.)
  	- [] Name
    - [] Phone Number
