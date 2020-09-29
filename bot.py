import trello
from flask import Flask, request

app = Flask(__name__)


@app.route("/add-to-waitlist", methods=["POST"])
def add_to_waitlist():
	print(request.values)

	# Trigger creating a card in Trello.


	return {
		"actions": {
			"say": "Added to waitlist."
		}
	}


if __name__ == "__main__":
	app.run()
