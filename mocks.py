"""Screen exhibits for the Lune site.

Each exhibit is a simplified drawing of a real LuneHub or merchant portal screen, built in HTML so it stays sharp
and readable at every width. One element in each exhibit is the key point (class ui__key) and one line states it.
Content rules: sample data only, offer merchants only from the Affiliate Programmes sheet, no city, cryptic raw text.
"""
import html

e = html.escape
LOGO = "img/logos/"
CHECK = '<svg class="ui__check" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def ui(inner, note):
    return f'<div class="ui">{inner}<p class="ui__note">{note}</p></div>'


def head(logo, title, sub, right=""):
    lg = f'<img class="ui__logo" src="{LOGO}{logo}" alt="">' if logo else ""
    return f'<div class="ui__head">{lg}<div class="ui__title"><b>{title}</b><span>{sub}</span></div><div class="ui__actions">{right}</div></div>'


def kpis(items, cols=4):
    out = ""
    for label, value, sub, key in items:
        k = " ui__key" if key else ""
        s = f"<small>{sub}</small>" if sub else ""
        out += f'<div class="ui__kpi{k}"><span>{label}</span><b>{value}</b>{s}</div>'
    return f'<div class="ui__kpis ui__kpis--{cols}">{out}</div>'


def table(cols, rows, cls=""):
    """cols: list of (label, kind) where kind is '', 'num', 'opt' or 'num opt'. rows: list of cell html."""
    h = "".join(f'<span class="ui__th {k}">{l}</span>' for l, k in cols)
    body = ""
    for r in rows:
        body += '<div class="ui__tr">' + "".join(f'<span class="ui__td {cols[i][1]}">{c}</span>' for i, c in enumerate(r)) + "</div>"
    return f'<div class="ui__table {cls}" style="--cols:{len(cols)}"><div class="ui__tr ui__tr--head">{h}</div>{body}</div>'


def brand(logo, name):
    return f'<span class="ui__brand"><img src="{LOGO}{logo}" alt="">{e(name)}</span>'


def bar(value, pct):
    return f'<span class="ui__barcell"><i style="--w:{pct}%"></i><em>{value}</em></span>'


def pill(text, kind=""):
    return f'<span class="ui__pill {kind}">{text}</span>'


def btn(text, kind=""):
    return f'<span class="ui__btn {kind}">{text}</span>'


# ------------------------------------------------------------------ ENRICH
TX = [
    ("POS PUR 448812 LVL SHS DXB MALL 00AE", "levelshoes.png", "Level Shoes", "Shopping › Clothing", "AED 1,032.00"),
    ("MAF HYPMKT MOE-0042 DXB ARE", "carrefour.png", "Carrefour", "Groceries › Supermarket", "AED 412.30"),
    ("ALSHAYA SBX 0921 DIFC GT AE", "starbucks.png", "Starbucks", "Dining › Coffeeshop", "AED 24.00"),
    ("NF* 8665797172 LOS GATOS 00012", "netflix.png", "Netflix", "Entertainment › Movie Streaming", "AED 56.99"),
    ("AL FUTTAIM HML 0291 DFC DXB", "ikea.png", "IKEA", "Shopping › Furniture", "AED 645.00"),
    ("FZ 1418829 T2 DXB AE 784", "flydubai.png", "flydubai", "Travel › Plane & Train Tickets", "AED 1,890.00"),
]
ENRICH_TX = ui(
    head("", "Transactions", "Each card description with its enriched result", pill("Real time", "ok")) +
    table([("From your bank", ""), ("Merchant", "ui__keycol"), ("Category", "opt"), ("Amount", "num opt2")],
          [[f'<code>{e(r)}</code>', brand(lg, m), c, a] for r, lg, m, c, a in TX], "ui__table--tx"),
    "Enrich names the merchant behind each card description.")

# ------------------------------------------------------------------ PULSE
OFFER = head("levelshoes.png", "Level Shoes · Designer shoes", "10% cashback, funded by Level Shoes", "{right}")

PULSE_LIVE = ui(
    OFFER.replace("{right}", pill("Live", "ok")) +
    '<div class="ui__strip"><b>Day 9 of 15</b><span>Ends 15 Oct 2026 · accepted by the Retail Offers team</span></div>' +
    kpis([("Eligible customers", "50,325", "", False), ("Activations", "6,492", "", False),
          ("Activation rate", "12.9%", "of eligible customers", True), ("Offer views", "20,130", "", False)]) +
    table([("Card programme", ""), ("Eligible customers", "barcol")],
          [["Gold credit", bar("31,905", 100)], ["Platinum credit", bar("18,420", 58)]], "ui__table--bars"),
    "One in eight eligible customers activated the offer. The merchant pays the cashback.")

PULSE_REVIEW = ui(
    OFFER.replace("{right}", pill("Review pending", "warn") + btn("Reject") + btn("Accept", "primary")) +
    kpis([("Cashback", "10%", "", False), ("Total budget", "AED 10,000", "paid by the merchant", False), ("Cap for each customer", "AED 150", "", False),
          ("Start date", "1 Oct 2026", "", False), ("End date", "15 Oct 2026", "", False), ("Refund window", "30 days", "", False)], 3) +
    table([("Card programme", ""), ("BIN", "opt"), ("Eligible customers", "num")],
          [[f'<span class="ui__on">{CHECK}Gold credit</span>', "<code>5311 22** ****</code>", "31,905"],
           [f'<span class="ui__on">{CHECK}Platinum credit</span>', "<code>4890 12** ****</code>", "18,420"],
           ['<span class="ui__off">Classic debit</span>', "<code>4005 51** ****</code>", '<span class="ui__mute">96,110</span>']]) +
    '<div class="ui__sum ui__key"><span>Selected reach · 2 of 3 card programmes</span><b>50,325 customers</b></div>',
    "Your team sees the terms and the reach, then accepts or rejects the offer.")

PULSE_CARDS = ui(
    head("", "Card Management", "Your registered card programmes", btn("Add new card", "primary")) +
    table([("Card programme", ""), ("BIN", "opt"), ("Cardholders", "num"), ("Active users", "num opt"), ("Live offers", "num ui__keycol")],
          [["Gold credit", "<code>5311 22** ****</code>", "31,905", "64%", "4"], ["Platinum credit", "<code>4890 12** ****</code>", "18,420", "71%", "4"],
           ["Classic debit", "<code>4005 51** ****</code>", "96,110", "48%", "3"], ["Wealth programme", "<code>6011 23** ****</code>", "4,260", "77%", "4"]]),
    "Register each card programme one time. Then select the programmes for each offer.")


def field(label, value, key=False):
    k = " ui__key" if key else ""
    return f'<div class="ui__field{k}"><span>{label}</span><b>{value}</b></div>'


MERCHANT_CREATE = ui(
    head("", "Create campaign", "Step 1 of 3 · Campaign details", btn("Save draft") + btn("Continue", "primary")) +
    '<div class="ui__chips"><span>Campaign goal</span><div>' +
    "".join(f'<span class="ui__chip{" is-on" if on else ""}">{t}</span>' for t, on in
            [("Acquire customers", False), ("Win back customers", True), ("Increase frequency", False), ("Grow average spend", False)]) + "</div></div>" +
    '<div class="ui__fields">' + field("Brand", "Level Shoes") + field("Campaign budget", "AED 10,000", True) + field("Cashback", "10%") +
    field("Cap for each customer", "AED 150") + field("Minimum spend", "AED 300") + field("Refund window", "30 days") + "</div>" +
    '<div class="ui__chips"><span>Budget use</span><div><span class="ui__chip is-on">Until the budget is spent</span><span class="ui__chip">Fixed dates</span></div></div>',
    "The merchant sets the goal and the budget. The merchant pays the cashback.")

MERCHANT_ANALYTICS = ui(
    head("levelshoes.png", "Level Shoes", "Campaign results · last 6 months", pill("3 campaigns")) +
    kpis([("Sales", "AED 412,600", "after refunds", False), ("Return on cashback", "9.1×", "sales for each AED 1", True),
          ("Cashback cost", "AED 45,340", "net of refunds", False), ("Customers rewarded", "1,486", "", False)]) +
    table([("Campaign", ""), ("Status", "opt"), ("Sales", "num"), ("Cost", "num opt"), ("Return", "num ui__keycol")],
          [["Designer shoes", pill("Live", "ok"), "AED 168,200", "AED 17,900", "9.4×"], ["New customer welcome", pill("Live", "ok"), "AED 131,950", "AED 16,920", "7.8×"],
           ["Eid collection", pill("Completed"), "AED 112,450", "AED 10,520", "10.7×"]]),
    "Each AED 1 of cashback brings AED 9.1 in sales for the merchant.")

# ------------------------------------------------------------------ ANALYTICS
FILTERS = '<div class="ui__filters">' + "".join(f"<span>{t}</span>" for t in ("AED", "Last 6 months", "All countries")) + "</div>"

DASH = ui(
    head("", "Dashboard", "Brand and category spend analytics", FILTERS) +
    kpis([("Customers", "412,880", "", False), ("Transactions", "18.6M", "", False), ("Total spend", "AED 3.94B", "", True), ("Spend per customer", "AED 9,543", "", False)]) +
    table([("Spend by category", ""), ("Total spend", "barcol")],
          [[n, bar(v, p)] for n, v, p in [("Shopping", "AED 698M", 100), ("Groceries", "AED 695M", 99), ("Dining", "AED 511M", 73), ("Travel", "AED 447M", 64),
                                           ("Household", "AED 399M", 57), ("Transportation", "AED 252M", 36)]], "ui__table--bars"),
    "Shopping and Groceries each take AED 0.7B of card spend in six months.")

BRANDS = ui(
    head("", "Brand Explorer", "All enriched brands", FILTERS) +
    table([("Brand", ""), ("Category", "opt"), ("Total spend", "barcol"), ("Customers", "num ui__keycol")],
          [[brand(lg, n), c, bar(s, p), cu] for lg, n, c, s, p, cu, sp in [
              ("carrefour.png", "Carrefour", "Groceries", "AED 96.2M", 100, "188,410", "AED 511"), ("amazon.png", "Amazon", "Shopping", "AED 88.4M", 92, "161,220", "AED 548"),
              ("starbucks.png", "Starbucks", "Dining", "AED 41.7M", 43, "152,036", "AED 274"), ("netflix.png", "Netflix", "Entertainment", "AED 27.9M", 29, "83,100", "AED 336"),
              ("ikea.png", "IKEA", "Shopping", "AED 21.7M", 23, "38,036", "AED 569"), ("uber.png", "Uber", "Transportation", "AED 18.3M", 19, "74,912", "AED 244")]], "ui__table--bars"),
    "Three brands each reach more than 150,000 of your customers.")

CATS = ui(
    head("", "Categories Explorer", "8 of 19 categories", FILTERS) +
    table([("Category", ""), ("Total spend", "barcol"), ("Customers", "num ui__keycol"), ("Subcategories", "num opt")],
          [[n, bar(s, p), cu, sc] for n, s, p, cu, tx, sc in [
              ("Shopping", "AED 698M", 100, "288,410", "4.1M", "9"), ("Groceries", "AED 695M", 99, "301,220", "9.2M", "6"), ("Dining", "AED 511M", 73, "296,905", "9.0M", "7"),
              ("Travel", "AED 447M", 64, "142,380", "0.6M", "4"), ("Household", "AED 399M", 57, "231,470", "2.1M", "7"), ("Transportation", "AED 252M", 36, "198,340", "3.8M", "11"),
              ("Wellness", "AED 215M", 31, "176,215", "1.4M", "7"), ("Entertainment", "AED 146M", 21, "214,905", "3.0M", "15")]], "ui__table--bars"),
    "Groceries and Dining reach the most customers. Travel has high spend from fewer customers.")

MOCKS = {
    "lunehub-transactions.jpg": ENRICH_TX,
    "lunehub-campaign-details-accepted.jpg": PULSE_LIVE,
    "lunehub-campaign-details-review-pending.jpg": PULSE_REVIEW,
    "lunehub-card-management.jpg": PULSE_CARDS,
    "merchant-create-campaign-step1.jpg": MERCHANT_CREATE,
    "merchant-analytics.jpg": MERCHANT_ANALYTICS,
    "lunehub-analytics-dashboard.jpg": DASH,
    "lunehub-analytics-brands.jpg": BRANDS,
    "lunehub-analytics-categories.jpg": CATS,
}
