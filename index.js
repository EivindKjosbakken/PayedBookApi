const express = require("express");
const app = express();

const stripe = require("stripe")(
	"sk_test_51Moy3uJaawNKBfql9Wi2DGlFU1398B2lG00Op3ZKrraVfpb6urCgx03ij6pverE7eOKkDk5JGdUiKDF3OdWhn8wb00boOtN0vu"
);

app.use(
	express.json({
		verify: (req, res, buffer) => (req["rawBody"] = buffer),
	})
);

////// Data Model ///////

// TODO Implement a real database
// Reverse mapping of stripe to API key. Model this in your preferred database.
const customers = {
	// stripeCustomerId : data
	stripeCustomerId: {
		apiKey: "123xyz",
		active: false,
		itemId: "stripeSubscriptionItemId",
	},
};
const apiKeys = {
	// apiKey : customerdata
	"123xyz": "stripeCustomerId",
	"6a6cd536035e87176af9fce1b91cf9c9e2ba665c8f28df77135db881b388387b":
		"stripeCustomerId",
};

const generateAPIKey = () => {
	const { randomBytes } = require("crypto");
	const apiKey = randomBytes(16).toString("hex");
	const hashedAPIKey = hashAPIKey(apiKey);

	if (apiKeys[hashedAPIKey]) {
		generateAPIKey();
	} else {
		return { hashedAPIKey, apiKey };
	}
};

// Hash the API key
const hashAPIKey = (apiKey) => {
	const { createHash } = require("crypto");

	const hashedAPIKey = createHash("sha256").update(apiKey).digest("hex");

	return hashedAPIKey;
};

// Create a Stripe Checkout Session to create a customer and subscribe them to a plan
app.post("/checkout", async (req, res) => {
	const session = await stripe.checkout.sessions.create({
		mode: "subscription",
		payment_method_types: ["card"],
		line_items: [
			{
				price: "price_1MoyHJJaawNKBfql8qzS71Ez",
			},
		],
		// {CHECKOUT_SESSION_ID} is a string literal; do not change it!
		// the actual Session ID is returned in the query parameter when your customer
		// is redirected to the success page.
		success_url:
			"http://YOUR-WEBSITE/dashboard?session_id={CHECKOUT_SESSION_ID}",
		cancel_url: "http://YOUR-WEBSITE/error",
	});

	res.send(session);
});

//NOTE: receives data from stripe when something happens
app.post("/webhook", async (req, res) => {
	let data;
	let eventType;
	// Check if webhook signing is configured.
	const webhookSecret =
		"whsec_24325783ceb7aff730863bcb68bf886e770bf78040a49249a8706dcfdf62bbf9"; //TODO you get this when you run: ".\stripe listen --forward-to localhost:8080/webh"
	console.log("Called");

	if (webhookSecret) {
		// Retrieve the event by verifying the signature using the raw body and secret.
		let event;
		let signature = req.headers["stripe-signature"];

		try {
			event = stripe.webhooks.constructEvent(
				req["rawBody"],
				signature,
				webhookSecret
			);
		} catch (err) {
			console.log(`⚠️  Webhook signature verification failed.`);
			return res.sendStatus(400);
		}
		// Extract the object from the event.
		data = event.data;
		eventType = event.type;
	} else {
		// Webhook signing is recommended, but if the secret is not configured in `config.js`,
		// retrieve the event data directly from the request body.
		data = req.body.data;
		eventType = req.body.type;
	}
	console.log("GOT HERE");
	switch (eventType) {
		//TODO do something for each type of event
		case "checkout.session.completed": //TODO error ere, does not happen
			console.log("Checkout session completed");
			console.log(data);
			// Data included in the event object:
			const customerId = data.object.customer;
			const subscriptionId = data.object.subscription;

			console.log(
				`💰 Customer ${customerId} subscribed to plan ${subscriptionId}`
			);

			// Get the subscription. The first item is the plan the user subscribed to.
			const subscription = await stripe.subscriptions.retrieve(
				subscriptionId
			);
			const itemId = subscription.items.data[0].id;

			// Generate API key
			const { apiKey, hashedAPIKey } = generateAPIKey();
			console.log(`User's API Key: ${apiKey}`);
			console.log(`Hashed API Key: ${hashedAPIKey}`);

			// Store the API key in your database. #store customer here
			customers[customerId] = {
				apikey: hashedAPIKey,
				itemId,
				active: true,
			};
			apiKeys[hashedAPIKey] = customerId;

			break;
		case "invoice.paid":
			// Continue to provision the subscription as payments continue to be made.
			// Store the status in your database and check when a user accesses your service.
			// This approach helps you avoid hitting rate limits.
			break;
		case "invoice.payment_failed":
			// The payment failed or the customer does not have a valid payment method.
			// The subscription becomes past_due. Notify your customer and send them to the
			// customer portal to update their payment information.
			break;
		default:
		// Unhandled event type
	}

	res.sendStatus(200);
});

// Get information about the customer
app.get("/customers/:id", (req, res) => {
	const customerId = req.params.id;
	const account = customers[customerId];
	if (account) {
		res.send(account);
	} else {
		res.sendStatus(404);
	}
});

// TODO this is where you should add the retrieve books plots stuff
app.get("/api", async (req, res) => {
	// const { apiKey } = "123"; //req.query;
	const apiKey = req.headers["x-api-key"]; // TODO api key in header like this line shows
	if (!apiKey) {
		console.log("You do not have api key");
		res.sendStatus(400).send("You do not have an API key"); // bad request
	}
	const hashedAPIKey = hashAPIKey(apiKey);
	const customerId = apiKeys[hashedAPIKey];

	const customer = customers[customerId];
	if (!customer || !customer.active) {
		res.sendStatus(403).send(
			"Forbidden access in /api endpoint, customer not found or not active from stripe"
		); // not authorized
	} else {
		// Record usage with Stripe Billing
		const record = await stripe.subscriptionItems.createUsageRecord(
			customer.itemId,
			{
				quantity: 1,
				timestamp: "now",
				action: "increment",
			}
		);
		res.send({ data: "fireship", usage: record });
	}
});

app.get("/usage/:customer", async (req, res) => {
	const customerId = req.params.customer;
	const invoice = await stripe.invoices.retrieveUpcoming({
		customer: customerId,
	});

	res.send(invoice);
});

app.listen(8080, () => console.log("alive on http://localhost:8080"));
