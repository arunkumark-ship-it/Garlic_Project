# 🧄 Garlic Order & Delivery Platform

Streamlit-based field operations app with role-based access:  
**Admin (master control) → Sales Executive (T1) → Delivery Driver (T2)**

## Project structure

```
garlic_app/
├── app.py                          ← Main router — run this
├── credentials.json                ← Your Google Service Account key (NOT in git)
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── config.toml                 ← Theme + server config
│   └── secrets.toml                ← For Streamlit Cloud (NOT in git)
├── utils/
│   ├── gsheet.py                   ← All Google Sheets read/write helpers
│   ├── auth.py                     ← Login, register, UID generation, hashing
│   └── style.py                    ← CSS + map embed helpers
└── pages/
    ├── login_page.py               ← Login + Register
    ├── admin/
    │   └── admin_dashboard.py      ← SKU, trips, driver assign, audit log
    ├── sales/
    │   ├── order_form.py           ← T1 order entry with customer auto-fill
    │   └── customer_onboard.py     ← Customer onboarding with map
    └── delivery/
        ├── route_view.py           ← T2 route execution, sequential stops
        └── driver_onboard.py       ← Driver onboarding with bank details
```

## Google Sheets tabs (auto-created)

| Sheet name | Purpose |
|---|---|
| `Base` | All orders + delivery updates |
| `Customer Onboard Data` | Customer registry (permanent CUST-IDs) |
| `Driver Onboard Data` | Driver registry (bank details, active status) |
| `SKU Master` | SKUs, prices, active/disabled |
| `Trips` | Trip-to-shop-to-driver assignments |
| `UserRegistry` | Login accounts (hashed passwords) |
| `sales executive` | SE-only registry |
| `delivery Driver` | Driver login registry |
| `Admin Log` | Full audit trail of admin actions |

## Local setup

### 1. Clone and install
```bash
git clone https://github.com/YOUR_USERNAME/garlic-app.git
cd garlic-app
pip install -r requirements.txt
```

### 2. Google credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → Enable **Google Sheets API** + **Google Drive API**
3. IAM & Admin → Service Accounts → Create → Add Key (JSON) → Download
4. Rename the downloaded file to **`credentials.json`** and place it in the project root
5. Open (or create) a Google Sheet named exactly:  
   **`Garlic_Order & Delivery Project`**
6. Share it with the `client_email` from credentials.json (Editor access)

### 3. Run
```bash
streamlit run app.py
```

All 9 sheet tabs are created automatically on first run.

## Streamlit Cloud deploy

1. Push repo to GitHub (**credentials.json is in .gitignore — never commit it**)
2. Go to [share.streamlit.io](https://share.streamlit.io) → Connect repo → main file: `app.py`
3. In **Advanced settings → Secrets**, paste the contents of your credentials.json in this format:

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

## Roles

| Role | What they can do |
|---|---|
| **admin** | SKU management, price control, trip builder, driver assignment, audit log |
| **sales executive** | Customer onboarding, place orders (auto Customer ID lookup), order history |
| **delivery Driver** | Driver onboarding, active toggle, route execution (sequential stops), delivery history |

## Key features

- **Auto Order ID** — `ORD-YYYYMMDD-XXXX` format, date-prefixed
- **Permanent IDs** — `CUST-XXXXXX`, `DD-XXXXXX`, `SE-XXXXXX`, `ADMIN-XXXXXX`
- **Customer auto-fill** — type Customer ID or mobile → all fields fill instantly
- **Duplicate prevention** — mobile used as unique key for customers and drivers
- **Price lock** — order stores price at time of entry; admin changes don't affect past orders
- **Active driver monitor** — admin sees only active (logged-in) drivers for assignment
- **Bank data masking** — account numbers shown as `****4521` in UI
- **Admin audit log** — every price change, SKU toggle, trip creation logged
- **Sequential route unlock** — driver must complete each stop before next unlocks
- **Live Google Maps** — shop location pinned for both sales and delivery screens
