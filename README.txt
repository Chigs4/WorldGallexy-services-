WORLDGALLEXY SERVICES — FRIEND TEST MVP

This is a local testable Flask MVP. It supports:
- customer job requests
- professional applications
- admin approval/rejection
- approved professional listing
- professional quotes
- quote viewing
- closing test jobs

TESTING ON ONE COMPUTER:
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run: python -m venv .venv
4. Activate the environment.
5. Run: pip install -r requirements.txt
6. Run: python app.py
7. Open http://127.0.0.1:5000

TESTING WITH FRIENDS ON THE SAME WI-FI:
1. Start the app on the host computer.
2. Find the host computer's local IPv4 address.
3. On phones connected to the same Wi-Fi, open http://HOST-IP:5000
4. Do NOT expose this server to the public internet.

ADMIN:
- http://HOST-IP:5000/admin
- Test PIN is 1234.
- Change WG_ADMIN_PIN before any broader deployment.

IMPORTANT:
- Use dummy test data only. Do not enter national ID numbers, passwords, bank details, or other sensitive information.
- This is NOT production-ready. It has no payment processing, secure identity verification, CSRF protection, rate limiting, robust authentication, encrypted sensitive-data storage, or production deployment hardening.
- For a real launch, use proper security/privacy design and involve a parent/guardian and qualified local legal/business professionals.
