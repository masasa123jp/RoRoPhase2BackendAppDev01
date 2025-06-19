import logging
import azure.functions as func
import stripe
import os

# Stripe のシークレットキーと署名検証用シークレット
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Stripe Webhook received a request.")

    payload = req.get_body()
    sig_header = req.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret
        )
    except ValueError as e:
        # 無効なペイロード
        logging.error(f"Invalid payload: {e}")
        return func.HttpResponse("Invalid payload", status_code=400)
    except stripe.error.SignatureVerificationError as e:
        # 署名の検証に失敗
        logging.error(f"Signature verification failed: {e}")
        return func.HttpResponse("Invalid signature", status_code=400)

    # イベントタイプに応じた処理
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        logging.info(f"PaymentIntent was successful: {payment_intent['id']}")
        # 必要な処理をここに追加
    else:
        logging.warning(f"Unhandled event type: {event['type']}")

    return func.HttpResponse(status_code=200)
