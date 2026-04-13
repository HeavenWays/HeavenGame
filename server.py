#!/usr/bin/env python3
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib import parse, request

PORT = int(os.getenv('PORT', '4173'))
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
PRICE_IDS = {
    'banniere': os.getenv('STRIPE_PRICE_BANNIERE', ''),
    'logo': os.getenv('STRIPE_PRICE_LOGO', ''),
    'pack': os.getenv('STRIPE_PRICE_PACK', ''),
}


class Handler(SimpleHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != '/api/create-checkout-session':
            self.send_error(404)
            return

        if not STRIPE_SECRET_KEY:
            self._json(500, {'error': 'STRIPE_SECRET_KEY manquante sur le serveur.'})
            return

        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            self._json(400, {'error': 'JSON invalide'})
            return

        offer = data.get('offer', '')
        email = data.get('email', '')
        price_id = PRICE_IDS.get(offer, '')
        if not price_id:
            self._json(400, {'error': f'Prix Stripe non configuré pour offre: {offer}'})
            return

        host = self.headers.get('Host', f'localhost:{PORT}')
        origin = f'http://{host}'
        params = {
            'mode': 'payment',
            'success_url': f'{origin}/checkout.html?success=1',
            'cancel_url': f'{origin}/checkout.html?canceled=1',
            'line_items[0][price]': price_id,
            'line_items[0][quantity]': '1',
        }
        if email:
            params['customer_email'] = email

        payload = parse.urlencode(params).encode('utf-8')
        req = request.Request(
            'https://api.stripe.com/v1/checkout/sessions',
            data=payload,
            method='POST',
            headers={
                'Authorization': f'Bearer {STRIPE_SECRET_KEY}',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )

        try:
            with request.urlopen(req, timeout=20) as resp:
                stripe_data = json.loads(resp.read().decode('utf-8'))
        except Exception as exc:
            self._json(502, {'error': f'Erreur Stripe API: {exc}'})
            return

        # Stripe returns URL for hosted checkout
        self._json(200, {
            'url': stripe_data.get('url'),
            'sessionId': stripe_data.get('id'),
            'publishableKey': STRIPE_PUBLISHABLE_KEY,
        })


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Server running on http://0.0.0.0:{PORT}')
    server.serve_forever()
