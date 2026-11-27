#!/usr/bin/env python3
"""Build the Lune website pages. Run: python3 build.py   (writes *.html next to this file)

Copy rules: ASD-STE100 at about 80%. Sentences of 20 words or fewer, active voice, present tense.
The build prints each sentence that breaks the length or punctuation rule.
"""
import html, re, sys
from mocks import MOCKS
from demos import AI_DEMO, SNIPS, CF_HOME, CF_IN, CF_TREND, EX_BRAND, EX_TX, phone_drawn, TIER_DEMO, LUNEHUB_DEMO, ANALYTICS_DEMO, DECODER, ENRICH_DEMO, JOURNEY, PULSE_DEMO, SCENE, drift, phones_demo
from pathlib import Path

ROOT = Path(__file__).parent
SALES = "https://sales.lunedata.io"
DOCS_API = "https://docs.lunedata.io/enrichment/enrichment-api"
DOCS_SDK = "https://docs.lunedata.io/pfm-sdk/"
LUNEHUB = "https://lunehub.lunedata.io/auth/login"
LIVE = "https://www.lunedata.io"
REVIEW = False  # shows the hero selector for review. Set to False before the site goes live.

# The navigation follows the product story: Enrich first, Pulse last.
NAV = [("enrich.html", "Enrich"), ("analytics.html", "Analytics"), ("expenses.html", "Expenses"),
       ("cashflow.html", "Cashflow"), ("pulse.html", "Pulse"), ("ai.html", "AI"), ("customers.html", "Customers")]

CLIENTS = [("adib.avif", "ADIB"), ("cbd.svg", "Commercial Bank of Dubai"), ("ajman-bank.png", "Ajman Bank"),
           ("nbf.avif", "National Bank of Fujairah"), ("uab.jpg", "United Arab Bank"), ("nbb.avif", "National Bank of Bahrain"),
           ("vision-bank.avif", "Vision Bank"), ("d360.avif", "D360 Bank"), ("beyon-money.avif", "Beyon Money"),
           ("alaan.avif", "Alaan"), ("tweeq.png", "Tweeq"), ("karty.png", "Karty"), ("myne.avif", "Myne"),
           ("sifi.avif", "Sifi"), ("afs.avif", "AFS"), ("simplifi.jpg", "Simplifi")]

e = html.escape


# ------------------------------------------------------------------ components
def page(slug, title, desc, body):
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{h}"{cur if h == slug else ""}>{t}</a>' for h, t in NAV)
    home = slug == "index.html"   # the home page is the landing design (landing_body.html, landing.css, landing.js)
    extra_head = '\n<link rel="stylesheet" href="landing.css">' if home else ""
    extra_js = '\n<script src="moon-gl.js"></script>\n<script src="landing.js"></script>' if home else '\n<script src="pages.js"></script>'
    return f"""<!DOCTYPE html>
<html lang="en"{" data-review" if REVIEW else ""}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" href="img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="ds/fonts/PlusJakartaSans-Latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="ds/tokens/fonts.css">
<link rel="stylesheet" href="ds/tokens/colors.css">
<link rel="stylesheet" href="ds/tokens/typography.css">
<link rel="stylesheet" href="ds/tokens/spacing.css">
<link rel="stylesheet" href="ds/tokens/base.css">
<link rel="stylesheet" href="site.css">
<link rel="stylesheet" href="v4.css">{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="site-head" data-nav>
  <div class="wrap site-head__row">
    <a class="brand" href="index.html"><img src="img/lune-logo.svg" alt="Lune" width="109" height="28"></a>
    <nav class="site-nav" id="site-nav" aria-label="Main">{nav}</nav>
    <div class="site-head__end">
      <a class="login" href="{LUNEHUB}">Log in</a>
      <a class="btn btn--dark btn--sm" href="contact.html">Talk to us</a>
      <button class="menu-btn" type="button" aria-label="Menu" aria-expanded="false" aria-controls="site-nav">≡</button>
    </div>
  </div>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="site-foot">
  <div class="wrap site-foot__grid">
    <div><a class="brand" href="index.html"><img src="img/lune-logo.svg" alt="Lune" width="94" height="24"></a><span class="muted" style="min-height:36px">© 2026 Lune Technologies</span>
      <a href="lune-privacy/">Privacy policy</a><a href="terms/">Terms</a><a href="cookie/">Cookie policy</a></div>
    <div><b>Products</b><a href="enrich.html">Enrich</a><a href="analytics.html">Analytics</a><a href="expenses.html">Expenses</a><a href="cashflow.html">Cashflow</a><a href="ai.html">AI assistant</a><a href="pulse.html">Pulse</a></div>
    <div><b>Pulse</b><a href="pulse.html#how">How Pulse works</a><a href="pulse.html#bank">For banks</a><a href="pulse.html#customer">For cardholders</a><a href="pulse.html#results">Results</a></div>
    <div><b>Company</b><a href="customers.html">Customers</a><a href="blog/">Blog</a><a href="contact.html">Contact sales</a></div>
    <div><b>Developers</b><a href="{DOCS_API}" target="_blank" rel="noopener">Enrichment API ↗</a><a href="{DOCS_SDK}" target="_blank" rel="noopener">Mobile SDK ↗</a><a href="{LUNEHUB}">Log in to LuneHub</a></div>
  </div>
  <div class="wrap"><p class="site-foot__note">Product screens on this site show sample data.</p></div>
</footer>
<script src="site.js"></script>{extra_js}
</body>
</html>
"""


def sec(inner, cls="", id_="", pre=""):
    attr = f' id="{id_}"' if id_ else ""
    return f'<section class="sec {cls}"{attr}>{pre}<div class="wrap stack">' + "\n" + inner + "\n</div></section>"


def head(eyebrow, h2, lead=""):
    p = f'<p class="lead">{lead}</p>' if lead else ""
    return f'<div class="head"><h2>{h2}</h2>{p}</div>'   # no small label above the headline


def hero(eyebrow, h1, lead, btns, side=""):
    grid = "hero__grid" if side else ""
    return f"""<section class="hero"><div class="wrap {grid}">
  <div class="hero__copy"><h1 class="h1--page">{h1}</h1><p class="lead">{lead}</p><div class="btns">{btns}</div></div>
  {side}
</div></section>"""


BTN_TALK = '<a class="btn btn--primary" href="contact.html">Talk to us</a>'
BTN_LIVE = f'<a class="btn btn--ghost" href="{SALES}" target="_blank" rel="noopener">Try Enrich live ↗</a>'


def shot(img, bar, cap, alt):
    if img in MOCKS:   # a drawn exhibit of the screen (mocks.py), not a capture
        return f"""<figure class="shot"><div class="shot__frame">
<div class="ui-wrap" role="img" aria-label="{e(alt)}">{MOCKS[img]}</div></div></figure>"""
    if img.endswith("cardholder-preview.jpg"):
        return f"""<figure class="shot"><div class="shot__frame">
<div class="dev dev--shot shot__dev"><div class="dev__scr"><img src="img/app/cust-03-offer.png" alt="{e(alt)}" loading="lazy"></div></div></div></figure>"""
    return f"""<figure class="shot"><div class="shot__frame">
<img src="img/product/{img}" alt="{e(alt)}" loading="lazy"></div></figure>"""


def phone(img, title, text):
    return (f'<figure class="phone"><div class="dev dev--shot"><div class="dev__scr"><img src="img/app/{img}" alt="{e(title)} screen" loading="lazy"></div></div>'
            f'<figcaption><b>{title}</b><span>{text}</span></figcaption></figure>')


def card(tag, h3, body, ticks=(), who="", link=None):
    t = f'<span class="tag">{tag}</span>' if tag else ""
    ul = '<ul class="ticks">' + "".join(f"<li>{x}</li>" for x in ticks) + "</ul>" if ticks else ""
    w = f'<span class="for">For: <b>{who}</b></span>' if who else ""
    ln = f'<a class="more" href="{link[0]}">{link[1]} →</a>' if link else ""
    return f'<div class="card">{t}<h3>{h3}</h3><p>{body}</p>{ul}{w}{ln}</div>'


def facts(items):
    return '<ul class="facts">' + "".join((f"<li><b>{a}</b> {b}</li>" if a else f"<li>{b}</li>") for a, b in items) + "</ul>"


def feature(eyebrow, h3, body, items, fig, wide=True, link=None):
    ln = f'<a class="more" href="{link[0]}">{link[1]} →</a>' if link else ""
    return f"""<div class="feature {'feature--wide' if wide else ''}"><div class="feature__copy"><h2 style="font-size:clamp(26px,2.6vw,38px)">{h3}</h2>
<p class="lead">{body}</p>{facts(items)}{ln}</div>{fig}</div>"""


def cta(h2, p, second=BTN_LIVE):
    second = second.replace("btn--ghost", "btn--ghost-ink")
    return f"""<section class="sec"><div class="wrap"><div class="cta"><h2>{h2}</h2><div class="cta__end"><p>{p}</p>
<div class="btns"><a class="btn btn--ink" href="contact.html">Talk to us</a>{second}</div></div></div></div></section>"""


def stats():
    return """<div class="stats">
<div><b>1.5 bn+</b><span>Transactions enriched each year</span></div>
<div><b>99%</b><span>Categorisation coverage</span></div>
<div><b>121+</b><span>Spend subcategories</span></div></div>"""


BADGES = '<div class="badges"><span>Certified and audited for regulated banks</span><span>ISO 27001</span><span>SOC 2 Type II</span><span>Dubai AI Seal</span><span>Hosted in UAE and KSA</span></div>'


def logos():
    hid = ' aria-hidden="true"'
    row = "".join(f'<img src="img/clients/{f}" alt="{e(a)}">' for f, a in CLIENTS)
    dup = "".join(f'<img src="img/clients/{f}" alt="">' for f, a in CLIENTS)   # second copy for the continuous slide
    return f'<div class="wrap logos" role="group" aria-label="Banks and fintechs that use Lune"><div class="logos__mask"><div class="logos__row">{row}<span class="logos__dup" aria-hidden="true">{dup}</span></div></div></div>'


TEST = ""   # one sample-data note sits in the page footer


def next_step(href, text):
    return f'<section class="sec"><div class="wrap"><div class="next"><span>The next Lune product</span><a href="{href}">{text} →</a></div></div></section>'


NEXT = {"enrich": next_step("analytics.html", "Analytics"), "analytics": next_step("expenses.html", "Expenses"),
        "expenses": next_step("cashflow.html", "Cashflow"), "cashflow": next_step("pulse.html", "Pulse"),
        "pulse": next_step("enrich.html", "Enrich").replace("The next Lune product", "Back to the first Lune product")}

# ------------------------------------------------------------------ HOME
FLOW = """<div class="flow dv" data-steps="700,1100,1100,1100,3400">
<div class="flow__step"><h3>Enrich names the payment</h3><span class="v flow__who"><img src="img/logos/levelshoes.png" alt="" width="40" height="40"><span><b style="color:#fff">Level Shoes</b><br>Shopping › Clothing</span></span></div>
<div class="flow__step"><h3>Your teams see the spend</h3><span class="v"><b style="color:#fff">AED 1,032.00</b><br>At Level Shoes, in LuneHub and Analytics</span></div>
<div class="flow__step"><h3>Your customer sees the merchant</h3><span class="v"><b style="color:#fff">Level Shoes</b><br>With logo and category, in Expenses</span></div>
<div class="flow__step flow__step--end"><h3>The customer earns cashback</h3><span class="big">AED 103.20</span><span class="v">Level Shoes pays the 10% cashback. Your bank gets the card spend and uses no rewards budget.</span></div>
</div>"""

HERO_COPY = f"""<h1>More card revenue.<br><span class="serif">From every transaction.</span></h1>
    <p class="lead">Lune turns the card transactions you already process into new revenue. Know where your customers spend, and let merchants pay to reach them.</p>
    <div class="btns">{BTN_TALK}<a class="btn btn--ghost" href="#how">See how it works</a></div>"""
FEED_NOTE = "Lune turns each card description into a merchant, a logo and a category."

# Three hero options. site.js shows one of them (draft option bar, or ?hero=a|b|c).
HEROES = f"""<section class="hero heroA" data-hero="a"><div class="heroA__grid" aria-hidden="true"></div>{drift(8, 3)}
<div class="wrap heroA__in">
    {HERO_COPY}
    {DECODER}
</div></section>
<section class="hero heroB" data-hero="b" hidden><div class="wrap hero__grid">
  <div class="hero__copy">
    {HERO_COPY}
  </div>
  <div class="scene-col">{SCENE}</div>
</div></section>
<section class="hero heroC" data-hero="c" hidden><div class="wrap heroC__in">
    {HERO_COPY}
    {JOURNEY}
</div></section>
"""
HEROES = HEROES.replace("</section>", "</section>" + logos() + "</div>").replace('<section class="hero hero', '<div class="first"><section class="hero hero').replace('<div class="first"><section class="hero heroB" data-hero="b" hidden>', '<div class="first" data-hero="b" hidden><section class="hero heroB">').replace('<div class="first"><section class="hero heroC" data-hero="c" hidden>', '<div class="first" data-hero="c" hidden><section class="hero heroC">').replace('<div class="first"><section class="hero heroA" data-hero="a">', '<div class="first" data-hero="a"><section class="hero heroA">')
# Hero B (3D card) is the default. The other two stay behind the review bar.
HEROES = HEROES.replace('<div class="first" data-hero="a">', '<div class="first" data-hero="a" hidden>').replace('<div class="first" data-hero="b" hidden>', '<div class="first" data-hero="b">')

# The solution in one picture: four separate products on one data set. Each card links to its chapter.
STEPS = [
    ("enrich", "01", "Name", "Enrich", "Each card payment gets a merchant name, a logo and a category.", "The foundation for each product"),
    ("analytics", "02", "See", "Analytics", "In LuneHub, your teams see each transaction and where customers spend.", "For your card and data teams"),
    ("in-app", "03", "Show", "PFM", "Expenses and Cashflow show your customers where their money goes, in your app.", "For your customers"),
    ("pulse", "04", "Earn", "Pulse", "Merchants fund the rewards. Customers earn only with your card, so they have a reason to pay with it.", "For your card revenue"),
]


PACK = {'enrich': 'Includes LuneHub', 'analytics': 'With Enrich or on its own', 'in-app': 'Two SDK modules', 'pulse': 'A separate product with its own SDK'}


def map_step(i, st):
    sid, n, verb, prod, text, who = st
    end = " map__step--end" if i == 3 else ""
    pack = PACK[sid]
    return f'<a class="map__step{end}" href="#{sid}"><span class="n"></span><b class="map__verb">{prod}</b><p>{text}</p></a>'


MAP = ('<div class="map">' + "".join(map_step(i, st) for i, st in enumerate(STEPS)) + "</div>"
       )

RAIL = ('<nav class="rail" aria-label="Lune products"><div class="wrap rail__row">'
        + "".join(f'<a href="#{st[0]}">{st[3]}</a>' for st in STEPS) + "</div></nav>")


def chapter(i, h2, lead, kv, buy, links, fig, cls=""):
    sid, n, verb, prod = STEPS[i][:4]
    rows = "".join(f"<div><b>{k}</b><span>{v}</span></div>" for k, v in kv)
    ln = "".join(f'<a class="more" href="{h}">{t} →</a>' for h, t in links)
    return f"""<section class="sec chapter {cls}" id="{sid}"><div class="wrap chapter__grid">
<div class="feature__copy chapter__copy"><h2 style="font-size:clamp(28px,3vw,44px)">{h2}</h2>
<p class="lead">{lead}</p><div class="kv">{rows}</div><div class="chapter__links">{ln}</div></div>
{fig}</div></section>"""


CHAPTERS = "\n".join([
    chapter(0, "Each card description gets a merchant name.",
            "Your bank sends card descriptions that customers cannot read. Enrich returns the merchant, logo and category in real time.",
            [("Merchant and logo", "The name your customer knows"), ("Category", "19 categories with subcategories"), ("Real time", "As each payment happens")],
            "<b>Enrich</b> is the foundation. It includes LuneHub, the portal for your teams.",
            [("enrich.html", "See how Enrich works")], ENRICH_DEMO, "sec--white"),
    chapter(1, "Your teams see where your customers spend.",
            "LuneHub lists each enriched transaction. Analytics shows spend by brand, category and customer.",
            [("Transactions", "Each payment with its merchant"), ("Brand explorer", "Spend and customers for each brand"), ("Category explorer", "All 19 Lune categories")],
            "<b>Analytics</b> runs in LuneHub. Buy it with Enrich or as a separate product.",
            [("analytics.html", "See all Analytics screens")], ANALYTICS_DEMO, "chapter--flip"),
    chapter(2, "Your customers see where their money goes.",
            "Expenses and Cashflow add ready screens to your iOS and Android app. Each payment shows a real merchant name and logo.",
            [("Expenses", "Spend by category and merchant"), ("Cashflow", "Money in against money out"), ("Your look", "Your colours, light and dark mode")],
            "<b>Expenses</b> and <b>Cashflow</b> are two separate SDK modules.",
            [("expenses.html", "See Expenses"), ("cashflow.html", "See Cashflow")], phones_demo("both"), "sec--white"),
    chapter(3, "Customers earn with your card. Merchants pay for the rewards.",
            "Pulse runs a rewards programme under your bank's name. Merchants fund each offer. Customers earn only with your card, so they have a reason to pay with it.",
            [("Your card", "Customers earn only with your card"), ("No rewards budget", "Merchants fund each reward"), ("Your control", "Your bank approves each offer")],
            "<b>Pulse</b> is a separate product. It includes the Pulse SDK for your app.",
            [("pulse.html", "See how Pulse works")], PULSE_DEMO, "chapter--flip"),
])

PROOF = '''
<div class="cols cols--2">
<figure class="quote"><blockquote>“We integrated Lune Enrich in a couple of months, with the team being responsive and helping every step of the way.”</blockquote>
<figcaption><img src="img/clients/d360.avif" alt="D360 Bank"><span><b>Masharty</b><i>Associate Director, D360 Bank</i></span></figcaption></figure>
<div style="display:grid;gap:20px">
<a class="case" href="customers.html#adib"><img src="img/clients/adib.avif" alt="ADIB" height="32"><b>ADIB shows customers where their money goes. →</b></a>
<a class="case" href="customers.html#nbf"><img src="img/clients/nbf.avif" alt="National Bank of Fujairah" height="32"><b>NBF replaced manual data work with structured insight. →</b></a>
</div></div>'''

PROBLEM = '''
<div class="points">
<div><h3>Customers do not recognise their payments</h3><p>Card statements show codes, not shop names. The customer cannot see where the money went.</p></div>
<div><h3>Your teams cannot see where customers spend</h3><p>Without merchant data, card and product teams cannot find the merchants that matter most.</p></div>
<div><h3>Your bank pays for every reward</h3><p>Each point and each cashback offer comes from your bank's budget. Merchants pay nothing.</p></div>
</div>'''

AI = f"""<section class="sec sec--white" id="ai"><div class="wrap chapter__grid">
<div class="feature__copy chapter__copy"><h2 style="font-size:clamp(28px,3vw,44px)">Customers ask about their money. <span class="serif">The assistant answers.</span></h2>
<p class="lead">The AI assistant is its own module in the Lune mobile SDK. It answers from the customer's enriched transactions.</p>
<div class="kv"><div><b>Plain questions</b><span>Customers ask in their own words</span></div><div><b>Real answers</b><span>Merchant names and categories from Enrich</span></div><div><b>Pulse offers</b><span>An offer that matches the customer's spend</span></div></div>
<div class="chapter__links"><a class="more" href="ai.html">See the AI assistant →</a></div></div>
{AI_DEMO}</div></section>"""

HOME = '<div class="lp">\n' + (ROOT / "landing_body.html").read_text(encoding="utf-8").replace("<!--SCENE-->", SCENE) + "\n</div>"   # hero B animation (3D card) from demos.py

# ------------------------------------------------------------------ ENRICH
RAW = [
    ("AMZ*MKTPL UK 2R45T LON GB 826", "amazon.png", "Amazon", "", "Shopping › Online marketplaces", "", "GBP 42.99"),
    ("POS 551204 MAF HYPMKT RYD PARK 682", "carrefour.png", "Carrefour", "كارفور", "Groceries › Supermarkets", "", "SAR 214.50"),
    ("CB INDITEX 3315 PARIS HAUSSM FR", "zara.png", "Zara", "", "Shopping › Clothing", "", "EUR 89.95"),
    ("UBR* PENDING 8005928996 NY 840", "uber.png", "Uber", "", "Transportation › Ride hailing", "", "USD 31.40"),
    ("IKANO PTE TMPNS 0291 SGP 702", "ikea.png", "IKEA", "宜家家居", "Home › Furniture", "", "SGD 189.00"),
    ("SBUX SHIBUYA TKY JP 392", "starbucks.png", "Starbucks", "スターバックス", "Dining › Cafés", "", "JPY 650"),
    ("NF* 8665797172 LOS GATOS 00012", "netflix.png", "Netflix", "نتفليكس", "Entertainment › Streaming", "Recurring", "AED 56.99"),
]
rawrows = "".join(f"""<div class="rawrow"><span class="rawrow__raw" data-ux-ignore="long-number-unchunked">{e(r)}</span><span class="rawrow__arrow">→</span>
<span class="rawrow__out"><img src="img/logos/{lg}" alt=""><span><b>{e(m)}{f' · {loc}' if loc else ''}</b><span><em>{cat}</em>{' · ' + city if city else ''} · {amt}</span></span></span></div>""" for r, lg, m, loc, cat, city, amt in RAW)

ENRICH = f"""{hero("Enrich", 'Every card payment, named: <span class="serif">merchant, logo and category.</span>',
 "Your core banking system sends a raw card description. AI-assisted Enrich returns the merchant, logo and category as the payment happens.",
 BTN_TALK + BTN_LIVE + f'<a class="btn btn--ghost" href="{DOCS_API}" target="_blank" rel="noopener">Read the API docs ↗</a>', ENRICH_DEMO)}

{sec(head("Sample transactions", "Enrich reads the card descriptions that customers cannot read.", "Seven card payments from seven countries. Enrich returns each result in real time.") + f'''
<div class="rawtable">{rawrows}</div>''')}

{sec(stats(), "sec--white")}

{sec(head("What you get back", "One API call returns four fields for each transaction.") + f'''
<div class="cols cols--4">
{card("", "Merchant name", "The name your customer knows, in all languages, from local and global merchant databases.")}
{card("", "Merchant logo", "A logo for each merchant, updated every day. Statements and apps show names that customers know.")}
{card("", "Category and subcategory", "19 consumer categories, each with subcategories. Examples are Groceries, Dining, Travel and Income.")}
{card("", "Recurring transactions", "Lune finds transactions that repeat. Examples are payments such as subscriptions and income such as a salary.")}
</div>''')}

{sec(feature("In LuneHub", "Your team sees each enriched transaction.", "LuneHub is the Lune portal for bank teams. It lists each transaction with its raw description and its enriched result.",
 [("Search", "by raw description or transaction ID."), ("Compare", "the raw description with the brand and category."), ("Flag", "a result that looks wrong.")],
 shot("lunehub-transactions-list.jpg", "LuneHub · Transactions", "", "LuneHub transactions list with raw description, brand, category, date and amount")), "sec--white")}

{sec(head("Built for banks", "Certified, audited and hosted in the UAE and Saudi Arabia.") + f'''
<div class="cols cols--4">
{card("", "ISO 27001", "Certified information security management.")}
{card("", "SOC 2 Type II", "Independent audit of security controls.")}
{card("", "Audit logs", "Lune logs every enrichment API call.")}
{card("", "Regional hosting", "Deployments in the UAE and Saudi Arabia, with disaster recovery.")}
</div>''')}

{NEXT["enrich"]}

{cta("See Enrich on your own transactions.", "Contact sales for a live demo on a sample of your transactions. Or enrich a sample feed in your browser now.")}
"""

# ------------------------------------------------------------------ ANALYTICS
def qa(title, items):
    rows = "".join(f"<div><b>{q}</b><span>{a}</span></div>" for q, a in items)
    return f'<div class="feature__copy"><h3>{title}</h3><div class="kv kv--qa">{rows}</div></div>'


BRAND_MORE = f'''
<div class="cols">
{card("Filter", "Find a brand in seconds", "Search by brand name. Filter by category. Set a range for spend, transactions, customers or spend per customer.")}
{card("Sort", "Rank brands your way", "Sort the list by spend, transactions, customers or spend per customer.")}
{card("Scope", "Select the period and the market", "Select a date range, a currency and a country. The list shows only that scope.")}
</div>
''' + qa("Questions the Brand explorer answers", [
    ("Which brands take most of our card spend?", "Sort by total spend."),
    ("Which brands do most of our customers use?", "Sort by customers."),
    ("Where is spend per customer high?", "Sort by spend per customer."),
    ("Which brands lead one category?", "Filter by category, then sort by spend."),
    ("Which merchants do we bring into Pulse first?", "Start with the brands that have the most customers."),
])

CATEGORY_MORE = f'''
<div class="cols">
{card("Filter", "Set a range for each metric", "Set a range for total spend, transactions or customers. The list shows the categories in that range.")}
{card("Sort", "Rank categories your way", "Sort the list by spend, transactions or customers.")}
{card("Scope", "Select the period and the market", "Select a date range, a currency and a country. The list shows only that scope.")}
</div>
''' + qa("Questions the Category explorer answers", [
    ("Where does our card spend go?", "Sort by total spend."),
    ("Which categories do most customers use?", "Sort by customers."),
    ("Which categories have many small payments?", "Compare transactions with total spend."),
    ("How does a category change by market?", "Change the country and compare."),
    ("Which categories do we target with offers?", "Start with the categories that have the most customers."),
])


ANALYTICS = f"""{hero("Analytics", 'See where your customers spend, <span class="serif">by merchant and category.</span>',
 "Analytics shows spend by merchant, category and customer from your AI-enriched transactions. Your teams get answers without a data request.", BTN_TALK, ANALYTICS_DEMO)}

{sec(feature("Overview", "See your card base and enriched volume at a glance.", "The Overview is the first screen in LuneHub. It shows how many cardholders transact and how many transactions Lune enriched.",
 [("Cardholders with transactions", "for the period you select."), ("Enriched transactions", "against the volume in your plan."), ("Transactions by date", "day by day, for the last month.")],
 shot("lunehub-overview.jpg", "LuneHub · Overview", "", "LuneHub overview with cardholders with transactions, enriched transactions against the plan, and transactions by date")), "sec--white")}

{sec(feature("Spend dashboard", "One view of customers, transactions and spend.", "Select a date range, a currency and a country. The dashboard shows the totals and the split.",
 [("Total customers", "and total transactions."), ("Total spend", "and spend per customer."), ("Spend by category and brand", "in one chart.")],
 shot("lunehub-dashboard.jpg", "LuneHub · Analytics · Dashboard", "", "LuneHub analytics dashboard with total customers, transactions, spend and spend per customer")), "sec--white")}

{sec(feature("Brand explorer", "Find the merchants where your customers spend most.", "The Brand explorer lists each enriched merchant with six columns. Your team filters and sorts the list to find the brands that matter.",
 [("Brand and category", "for each enriched merchant."), ("Total spend and transactions", "for the period you select."), ("Customers", "who paid that brand with your cards."), ("Spend per customer", "to compare brands of different size.")],
 shot("lunehub-analytics-brands.jpg", "LuneHub · Analytics · Brands", "The Brand explorer in LuneHub. " + TEST, "LuneHub brand explorer with spend, transactions, customers and spend per customer for each brand")) + BRAND_MORE)}

{sec(feature("Category explorer", "See spend for each category.", "The Category explorer lists all 19 Lune categories with their totals. Your team sees where card spend goes and how many customers are behind it.",
 [("Total spend and transactions", "for each category."), ("Customers", "who spend in each category."), ("The number of subcategories", "below each category.")],
 shot("lunehub-analytics-categories.jpg", "LuneHub · Analytics · Categories", "The Category explorer in LuneHub, with the first eight of 19 categories. " + TEST, "LuneHub category explorer with spend, transactions, customers and subcategories")) + CATEGORY_MORE, "sec--white")}

{sec('''<div class="split"><div class="head"><h2>Spend data shows which merchants can <span class="serif">fund your rewards.</span></h2></div>
<div class="feature__copy"><p class="lead">The Brand explorer shows the merchants where your customers spend most. Through Pulse, those merchants fund cashback for your customers.</p>''' + facts([("One portal.", "Analytics and Pulse share one LuneHub sign-in."), ("One data set.", "Pulse audiences come from the same enriched transactions."), ("Your data only.", "Each bank sees its own customers and transactions.")]) + '''<a class="more" href="pulse.html">See Pulse →</a></div></div>''', "sec--teal")}
{NEXT["analytics"]}

{cta("See your own spend data in LuneHub.", "We show Analytics with sample data, or with a sample of your own enriched transactions.")}
"""

# ------------------------------------------------------------------ EXPENSES / CASHFLOW
BTN_SDK = f'<a class="btn btn--ghost" href="{DOCS_SDK}" target="_blank" rel="noopener">SDK docs ↗</a>'
IN_APP = f'''<div class="cols">
{card("", "Your look", "Your colours, light and dark mode, and your currency.")}
{card("", "Two platforms", "Native SDKs for iOS and Android.")}
{card("", "Enriched by AI", "Each transaction shows the merchant name, logo and category from AI-assisted Lune Enrich.")}
{card("", "AI assistant", "A separate module in the same SDK. Customers ask about their money in their own words.")}
</div>'''

EXPENSES = f"""{hero("Expenses", 'Show customers where <span class="serif">their money goes.</span>',
 "Expenses adds ready spending screens to your iOS and Android app. Customers see spend by merchant and category. The AI assistant answers their questions about it.", BTN_TALK + BTN_SDK, phones_demo("exp"))}

{sec(head("Expenses screens", "Payments show real merchant names and categories.") + f'''
<div class="phones">
{phone("exp-home.png", "This month", "Spending day by day, against last month.")}
{phone("exp-all.png", "Every transaction", "Search by merchant, category or amount.")}
{phone_drawn(EX_TX, "One payment", "Merchant, category, tags and feedback.")}
</div>''', "sec--white")}

{sec(head("Trends", "Customers follow each category and each brand over time.", "Two trend pages show where the money goes. A customer opens a category or a brand to see its history.") + f'''
<div class="phones">
{phone("exp-cats.png", "Category trends", "Top categories with spend and share of spend.")}
{phone("exp-brands.png", "Brand trends", "Spend for each day and the top brands.")}
{phone_drawn(EX_BRAND, "One brand", "Six months of spend with that brand.")}
</div>''')}

{sec(head("What customers can do", "Customers see their spend and plan their month.") + f'''
<div class="cols cols--4">
{card("", "Spend by category", "For this month, last month, the last three months or this year.")}
{card("", "Search and filter", "Search by merchant, category or amount. Filter the list by category or tag.")}
{card("", "Budgets", "Budgets by category or in total, with progress for the month.")}
{card("", "Feedback", "A customer can report a wrong merchant or category on a transaction.")}
</div>''', "sec--white")}

{sec(head("In your app", "Native screens for iOS and Android.") + IN_APP)}

{NEXT["expenses"]}

{cta("See Expenses in a sample bank app.", "Contact sales for a live demo of Expenses on sample data.", BTN_SDK)}
"""

CASHFLOW = f"""{hero("Cashflow", 'Show customers money in <span class="serif">against money out.</span>',
 "Cashflow adds ready screens to your iOS and Android app. Customers compare money in with money out. The AI assistant answers their questions about it.", BTN_TALK + BTN_SDK, phones_demo("cf"))}

{sec(head("Cashflow screens", "Customers compare money in with money out.") + f'''
<div class="phones">
{phone_drawn(CF_HOME, "Total cashflow", "Money in against money out for one salary month.")}
{phone_drawn(CF_IN, "Money in", "Sources by type: income, transfers in and government services.")}
{phone_drawn(CF_TREND, "Trends", "Six months of money in and out, with a summary.")}
</div>''', "sec--white")}

{sec(head("What customers can do", "Customers see where money comes from and where it goes.") + f'''
<div class="cols">
{card("", "Inflow and outflow", "Money in and money out for a period, with transaction counts.")}
{card("", "Smart insights", "Insights in plain language, such as the cashflow summary.")}
{card("", "Cashflow history", "A timeline of inflow and outflow, month by month.")}
</div>''')}

{sec(head("In your app", "Native screens for iOS and Android.") + IN_APP, "sec--white")}

{NEXT["cashflow"]}

{cta("See Cashflow in a sample bank app.", "Contact sales for a live demo of Cashflow on sample data.", BTN_SDK)}
"""

# ------------------------------------------------------------------ PULSE
PULSE_H1 = "Rewards under your bank's name. " + '<span class="serif">Merchants pay.</span>'
BTN_HOW = '<a class="btn btn--ghost" href="#how">See how it works</a>'
PULSE = f"""{hero("Pulse", PULSE_H1,
 "Pulse is a rewards programme for your customers. Merchants fund the offers. An AI recommendation engine shows each customer the offers that fit their spend. Your bank approves them.", BTN_TALK + BTN_HOW, PULSE_DEMO)}

{sec(head("Why card managers use Pulse", "Customers earn with your card. Merchants pay for the rewards.") + f'''
<div class="cols">
{card("Targeting", "AI recommends each offer", "Lune builds each audience from your enriched transactions. An AI recommendation engine shows each customer the offers that fit their spend.")}
{card("Card spend", "Customers earn only with your card", "A customer activates an offer in your app. The customer then earns on purchases with your card.")}
{card("Cost", "Merchants fund each reward", "The merchant sets the budget, the cashback rate and the cap. Your bank needs no rewards budget.")}
{card("Control", "Your bank approves each offer", "Your team sees the terms, the stores and the audience. Your team chooses the cards that can earn.")}
</div>''', "sec--white")}

{sec(head("How Pulse works", "Four parties. One offer.", "Each offer moves from the merchant to Lune, to your bank, then to your customer.") + '''
<div class="party">
<div><b>Merchant creates</b><span>Sets the budget, cashback rate, cap and stores.</span></div>
<div><b>Lune targets</b><span>Builds the offer and selects eligible customers from enriched spend.</span></div>
<div><b>Bank approves</b><span>Accepts or rejects the offer and chooses the cards.</span></div>
<div><b>Customer earns</b><span>Joins, activates the offer in the app and pays by card.</span></div>
</div>''', id_="how")}

{sec(feature("01 · Merchant creates", "Merchants create campaigns in their own portal.", "A merchant sets up a campaign and sends it for review. The merchant pays cashback only on purchases that meet the terms.",
 [("Goal and budget.", "A goal, a total budget, the cashback rate, a cap and a minimum spend."), ("Two budget modes.", "Run until the budget is spent, or run for fixed dates."), ("Each brand and store.", "Several brands, with merchant IDs and terminal IDs.")],
 shot("merchant-create-campaign-step1.jpg", "Pulse merchant portal · Create campaign", "Step 1 of the campaign form in the merchant portal. " + TEST, "Merchant portal create campaign form with goal, budget, cashback percentage, cap and dates")), "sec--white", "merchant")}

{sec(head("02 · Lune targets", 'Each offer reaches the customers who <span class="serif">match the goal.</span>', "The merchant selects a goal for the campaign. Lune builds the audience for that goal from your enriched transactions.") + f'''
<div class="cols cols--4">
{card("Acquire customers", "New to the brand", "They spend in the category, but not at this brand.")}
{card("Win back customers", "Stopped buying", "They bought from the brand, then stopped.")}
{card("Increase frequency", "Buy now and then", "They buy from the brand, but not often.")}
{card("Grow average spend", "Small baskets", "They spend a low amount on each purchase.")}
</div>
<div style="display:grid;gap:16px"><p class="tag">More ways to target</p>
<div class="cols">
{card("", "By category", "One category or subcategory, such as Dining or Food Delivery.")}
{card("", "By spend level", "Above or below an amount, such as AED 2,000 on Travel in six months.")}
{card("", "By card programme", "Only the cards your team selects, such as Platinum credit.")}
</div>
</div>''' + '<div class="split split--top"><div class="feature__copy">' + facts([("Audience size first.", "Your team sees how many customers can earn before the offer goes live."), ("Your data stays yours.", "Each bank's audience comes from its own customers and transactions.")]) + '</div><div class="feature__copy">' + facts([("Terms written for you.", "Lune writes the offer terms from the campaign settings."), ("No work for your data team.", "Lune builds each audience. Your team approves the offer.")]) + '</div></div>', "sec--teal", "targeting")}

{sec(feature("03 · Bank approves", "No offer goes live without your approval.", "The offer arrives in the Campaign Manager in LuneHub. Your team sees the terms, the stores and the audience.",
 [("One inbox.", "Pending, accepted, completed and rejected offers, with search."), ("Accept or reject.", "One decision for each offer."), ("Clear terms.", "Cashback rate, budget, cap, dates and refund window.")],
 shot("lunehub-campaign-details-review-pending.jpg", "LuneHub · Campaign Manager · Campaign details", "An offer that waits for the bank's decision in LuneHub. " + TEST, "LuneHub campaign details with Reject and Accept buttons")) + f'''
<div class="cols cols--2">
{shot("lunehub-card-management.jpg", "LuneHub · Card Management", "Register card programmes by BIN. Select which programmes can earn on each offer. " + TEST, "LuneHub card management with card programmes, BIN, active users and cardholders")}
{shot("lunehub-campaign-details-review-pending-tab-cardholder-preview.jpg", "Customer app · Offer", "See the offer and its terms as your customers see them. " + TEST, "LuneHub cardholder preview of an offer on a phone")}
</div>''', "sec--white", "bank")}

{sec(head("04 · Customer journey", "Customers join once, activate offers with one tap and track their rewards.", "Pulse runs in your mobile app through the Lune SDK for iOS and Android. It uses your bank's name and colour.") + f'''
<div class="phones">
{phone("cust-01-join.png", "Join", "The customer reads the terms and joins.")}
{phone("cust-02-home.png", "Offers", "The offers for the customer's card.")}
{phone("cust-03-offer.png", "Read the offer", "Minimum spend, maximum cashback and end date.")}
{phone("cust-04-activated.png", "Activate and pay", "One tap. Then the customer pays by card.")}
{phone("cust-05-rewards.png", "Track rewards", "Cashback this month, payable and pending.")}
{phone("cust-06-tiers.png", "Tiers", "The customer earns more at each tier.")}
</div>''', id_="customer")}

{sec(head("Offer types", "Card-linked, affiliate and promo-code offers in one programme.", "Your customers see each offer type in the same place in your app.") + f'''
<div class="cols">
{card("", "Card-linked offers", "Merchant-funded cashback. The customer activates the offer, then pays by card in store or online.")}
{card("", "Affiliate offers", "Cashback from online brands through affiliate networks. The customer shops through the offer link.")}
{card("", "Promo codes", "Discount codes from online brands. The customer copies the code and uses it at checkout.")}
</div>''' + head("Reward types", "Cashback or points, with tiers and missions.", "You choose how your customers earn.") + f'''
<div class="cols cols--4">
{card("", "Cashback", "Customers earn money back on each eligible purchase.")}
{card("", "Points", "Customers earn points and redeem them for cash value. You set the expiry dates.")}
{card("", "Tiers", "Customers move up tiers on the points they earn in 12 months.")}
{card("", "Missions and badges", "Bonus rewards for repeat spend, such as five purchases in a month.")}
</div><div class="solo">{TIER_DEMO}</div>''', "sec--white")}

{sec(head("Results", "Your bank and the merchant each see the result of each offer.", "The bank view is in LuneHub. The merchant view is in the merchant portal.") + f'''
<div class="cols cols--2">
{shot("lunehub-campaign-details-accepted.jpg", "LuneHub · Live offer", "Bank view: audience, activations, activation rate and offer views. " + TEST, "LuneHub live offer with total audience, offer activations, activation rate and offer views")}
{shot("merchant-analytics.jpg", "Pulse merchant portal · Analytics", "Merchant view: sales, return on cashback and net cashback cost. " + TEST, "Merchant portal analytics with sales, return on cashback and cashback cost")}
</div>''' + '<div class="split split--top"><div class="feature__copy"><h3>For your bank</h3>' + facts([("Reach and activation.", "Audience, activations, activation rate and offer views for each offer."), ("Reach by card programme.", "Cardholders, active users and live offers for each BIN."), ("Clear record.", "Who accepted each offer and when.")]) + '</div><div class="feature__copy"><h3>For the merchant</h3>' + facts([("Sales after refunds.", "Sales that earned cashback for each campaign."), ("Return on cashback.", "Sales for each unit of cashback spent."), ("Net cashback cost.", "Cashback accrued minus cashback reversed by refunds.")]) + '</div></div>', id_="results")}

{sec(head("Cashback you can trust", "Lune checks each purchase against the offer terms.") + f'''
<div class="cols cols--4">
{card("", "Budgets stay in limits", "A campaign closes when its budget runs out. No customer earns more than the cap.")}
{card("", "Refunds handled", "A refund in the refund window reduces the cashback.")}
{card("", "Confirmed after the window", "Cashback becomes final when the refund window ends.")}
{card("", "A full record", "Each purchase has a recorded result, with the reason when it does not earn.")}
</div>''', "sec--white")}

{NEXT["pulse"]}

{cta("See one offer go from merchant to customer.", "Contact sales for a live demo. It runs one campaign through the merchant portal, LuneHub and the customer app.", '<a class="btn btn--ghost" href="customers.html">See customers</a>')}
"""

# ------------------------------------------------------------------ CUSTOMERS
STUDIES = [
    ("adib", "adib.avif", "ADIB", "Retail bank · UAE", "ADIB shows customers where their money goes.",
     [("Client", "Abu Dhabi Islamic Bank"), ("Lune products", "Enrich, personal finance SDK"), ("Category accuracy", "98%")],
     "ADIB wanted to give customers useful insight into their spending. Raw transaction descriptions were not clear. Too many transactions had no category.",
     "Enrich adds the merchant name, logo, category and subcategory to each transaction. The Lune SDK gives ADIB ready personal finance screens.",
     ["Customers see the real merchant behind each payment.", "Customers track spending, saving and goals in the ADIB app.", "ADIB can build merchant offers on the same data."], ""),
    ("d360", "d360.avif", "D360 Bank", "Digital bank · Saudi Arabia", "D360 shows the real merchant behind each card payment.",
     [("Client", "D360 Bank"), ("Lune products", "Enrich"), ("Category accuracy", "98%"), ("Time to integrate", "About 2 months")],
     "Many card transactions in the region show a holding-company name, not the store. Customers cannot see where their money goes.",
     "D360 integrated the Enrich API. Each transaction now shows the merchant name, a logo and an accurate category.",
     ["Customers recognise where their money goes.", "D360 personalises its app from clean, categorised data."],
     "“We integrated Lune Enrich in a couple of months, with the team being responsive and helping every step of the way.” Masharty, Associate Director, D360 Bank"),
    ("nbf", "nbf.avif", "National Bank of Fujairah", "Retail bank · UAE", "NBF replaced manual data work with structured insight.",
     [("Client", "National Bank of Fujairah"), ("Lune products", "Enrich, Analytics")],
     "NBF staff read unstructured transaction rows by hand to understand customer spend. The work was slow and hard to scale.",
     "Lune enriches NBF's transactions and gives structured spend insight by merchant and category.",
     ["Teams make decisions faster and with more accurate data.", "NBF builds more personalised services for corporate clients.", "Faster data processing reduces operating cost."], ""),
    ("beyon-money", "beyon-money.avif", "Beyon Money", "Digital wallet · Bahrain", "Beyon Money launched in-app insights in under three months.",
     [("Client", "Beyon Money"), ("Lune products", "Enrich, Analytics"), ("Start to go-live", "Under 3 months")],
     "Beyon Money wanted one app where users see their spending by category in real time. Central Bank of Bahrain data-storage rules also applied.",
     "Enrich categorises each transaction in real time. Lune deployed the platform to meet local data-storage rules.",
     ["Users spend more time in the app.", "Users understand their finances better.", "Beyon Money can add merchant offers on the same data."], ""),
    ("alaan", "alaan.avif", "Alaan", "Fintech · UAE", "Alaan gave SME card users clear transaction insight.",
     [("Client", "Alaan"), ("Lune products", "Enrich")],
     "Alaan issues corporate cards for SMEs in the UAE. It wanted to remove manual work and give customers clearer transactions.",
     "Alaan integrated the Enrich API. Each card transaction now shows the merchant name, logo and a detailed category.",
     ["Alaan shipped transaction insights faster.", "Finance teams see who they paid and for what."], ""),
]


def study(s):
    sid, logo, name, kind, title, dl, ch, dv, out, quote = s
    d = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in dl)
    q = f'<p style="font-weight:600;letter-spacing:-0.01em;font-size:22px;line-height:1.3;color:var(--lune-teal)">{quote}</p>' if quote else ""
    return f"""<article class="card study" id="{sid}"><img class="logo" src="img/clients/{logo}" alt="{e(name)}"><span class="tag">{kind}</span><h3 class="h2" style="font-size:clamp(24px,2.4vw,34px)">{title}</h3>
<dl>{d}</dl><div class="cols"><div><h4 style="margin:0 0 6px">The challenge</h4><p>{ch}</p></div><div><h4 style="margin:0 0 6px">What Lune delivered</h4><p>{dv}</p></div>
<div><h4 style="margin:0 0 6px">The outcome</h4>{facts([(o, "") for o in out])}</div></div>{q}</article>"""


CUSTOMERS = f"""{hero("Customers", 'Banks and fintechs that <span class="serif">run on Lune data.</span>',
 "Retail banks, digital banks and fintechs in the UAE, Saudi Arabia and Bahrain use Lune. AI-assisted enrichment makes their transactions clear to customers and to their teams.", BTN_TALK)}
<section><div class="wrap">{logos().replace('<div class="wrap logos">', '<div class="logos" style="margin-top:0">')}</div></section>
{sec(head("Case studies", "Five clients. One result: clear transactions.") + '<div class="stack" style="gap:20px">' + "".join(study(s) for s in STUDIES) + "</div>" + stats())}
{cta("Your bank can be the next case study.", "Contact sales for a live demo on sample data, then on a sample of your own transactions.")}
"""

# ------------------------------------------------------------------ CONTACT
PRODUCTS = ["Enrich", "Analytics", "Expenses", "Cashflow", "Pulse", "Not sure yet"]
COUNTRIES = ["United Arab Emirates", "Saudi Arabia", "Bahrain", "Qatar", "Kuwait", "Oman", "Egypt", "Jordan", "Other"]
CONTACT = f"""{hero("Contact sales", 'Talk to our sales team about <span class="serif">a live demo.</span>',
 "Tell us about your bank and what you want to see. We show Lune on sample data, then on a sample of your own transactions.", "")}
{sec(f'''<div class="split split--top">
<form class="form card" id="contact-form" novalidate>
<div class="form__row">
<div class="field" data-field="first"><label for="f-first">First name</label><input id="f-first" name="first" enterkeyhint="next" autocomplete="given-name" required><span class="err">Enter your first name.</span></div>
<div class="field" data-field="last"><label for="f-last">Last name</label><input id="f-last" name="last" enterkeyhint="next" autocomplete="family-name" required><span class="err">Enter your last name.</span></div>
</div>
<div class="form__row">
<div class="field" data-field="email"><label for="f-email">Work email</label><input id="f-email" name="email" enterkeyhint="next" type="email" inputmode="email" autocomplete="email" required><span class="err">Enter a work email, for example name@bank.com.</span></div>
<div class="field" data-field="company"><label for="f-company">Company</label><input id="f-company" name="company" enterkeyhint="next" autocomplete="organization" required><span class="err">Enter your company name.</span></div>
</div>
<div class="form__row">
<div class="field"><label for="f-title">Job title (optional)</label><input id="f-title" name="title" enterkeyhint="next" autocomplete="organization-title"></div>
<div class="field"><label for="f-country">Country</label><select id="f-country" name="country" autocomplete="country-name">{"".join(f"<option>{c}</option>" for c in COUNTRIES)}</select></div>
</div>
<fieldset class="field" data-field="product"><legend>What do you want to see?</legend><div class="checks">{"".join(f'<label><input type="checkbox" name="product" value="{p}">{p}</label>' for p in PRODUCTS)}</div><span class="err">Select at least one product.</span></fieldset>
<div class="field"><label for="f-notes">Other information for our sales team (optional)</label><textarea id="f-notes" name="notes"></textarea></div>
<p class="small">We use your details only to reply to this request. See our <a href="{LIVE}/lune-privacy">privacy policy</a>.</p>
<div><button class="btn btn--primary" type="submit">Send request</button></div>
<p id="form-done" hidden><b>Your email app opens with the request.</b> Send the email to complete the request.</p>
</form>
<div class="stack" style="gap:24px">
<div class="card card--muted"><h2 class="h3">What happens next</h2>{facts([("", "Our sales team replies to your request."), ("", "We agree a time for a live demo."), ("", "We show the products you selected on sample data.")])}</div>
<div class="card card--muted"><h2 class="h3">Your data</h2><p>The first demo uses sample data only. Lune is ISO 27001 certified and has a SOC 2 Type II report.</p></div>
<div class="card card--muted"><h2 class="h3">Contact details</h2><p><a href="mailto:hello@lunedata.io">hello@lunedata.io</a></p><p>156 Gate Avenue, DIFC<br>Dubai, United Arab Emirates</p>
<a class="more" href="{SALES}" target="_blank" rel="noopener">Try Enrich live ↗</a></div>
</div></div>''')}
"""

AI_PAGE = f"""{hero("AI assistant", 'Customers ask about their money. <span class="serif">The assistant answers.</span>',
 "The AI assistant is its own module in the Lune mobile SDK. It answers from the customer's enriched transactions and shows Pulse offers that match their spend.", BTN_TALK + BTN_SDK, AI_DEMO)}

{sec(head("What customers ask", "Each question gets an answer from real payments.", "Four example questions.") + f'''
<div class="snips">{SNIPS}</div>''', "sec--white")}

{sec(head("For your bank", "The assistant uses products your bank controls.") + f'''
<div class="cols cols--4">
{card("", "In your app", "The assistant is a separate module in the Lune mobile SDK. It uses your colours.")}
{card("", "The customer's own data", "Each answer comes from that customer's enriched transactions.")}
{card("", "Offers you approve", "The assistant shows Pulse offers. Your bank approves each offer.")}
{card("", "Merchant-funded rewards", "The merchant funds each reward. Your bank uses no rewards budget.")}
</div>''')}

{cta("See the AI assistant in a sample bank app.", "Contact sales for a live demo of the assistant on sample data.", BTN_SDK)}
"""

PAGES = [
    ("index.html", "Lune | More card revenue from every transaction", "Lune turns the card transactions you already process into new revenue. Know where your customers spend, and let merchants pay to reach them.", HOME),
    ("enrich.html", "Enrich | Real-time transaction enrichment API | Lune", "Enrich returns the merchant, logo and category for each card transaction as it happens.", ENRICH),
    ("analytics.html", "Analytics | Spend by merchant and category | Lune", "Analytics shows spend by merchant, category and customer from your AI-enriched transactions.", ANALYTICS),
    ("expenses.html", "Expenses | Spending screens for your app | Lune", "Expenses adds ready spending screens to your iOS and Android app, with an AI assistant module.", EXPENSES),
    ("cashflow.html", "Cashflow | Money in against money out | Lune", "Cashflow adds ready screens to your iOS and Android app, with an AI assistant module.", CASHFLOW),
    ("pulse.html", "Pulse | Merchant-funded rewards under your bank's name | Lune", "Pulse is a rewards programme for your customers. Merchants fund the offers. Your bank approves them.", PULSE),
    ("ai.html", "AI assistant | Lune", "An AI assistant module in the Lune mobile SDK. It answers from enriched transactions and shows Pulse offers that match spend.", AI_PAGE),
    ("customers.html", "Customers | Banks and fintechs on Lune", "Case studies from ADIB, D360 Bank, National Bank of Fujairah, Beyon Money and Alaan.", CUSTOMERS),
    ("contact.html", "Contact sales | Lune", "Talk to the Lune sales team about a live demo.", CONTACT),
]


# ------------------------------------------------------------------ copy check (STE)
def ste_check(slug, body):
    t = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", body)
    t = re.sub(r"</(p|h\d|li|span|div|b|a|dt|dd|figcaption|button|label|legend|option|blockquote)>", ". ", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    issues = []
    for s in re.split(r"(?<=[.!?])\s+", t):
        s = s.strip(" .")
        words = [w for w in s.split() if re.search(r"[A-Za-z]", w)]
        if len(words) > 20 and "“" not in s:          # customer quotes stay as spoken
            issues.append(f"{len(words)} words: {s[:110]}")
        if re.search(r"[;—–]", s):
            issues.append(f"punctuation: {s[:110]}")
    for i in issues:
        print(f"  STE {slug}: {i}")
    return len(issues)


# ------------------------------------------------------------------ BLOG (imported from the old site by import_blog.py)
import json
from datetime import date as _date

POSTS = sorted((json.loads(f.read_text(encoding="utf-8")) for f in (ROOT / "content" / "blog").glob("*.json")),
               key=lambda p: (p["date"], p["title"]), reverse=True)


def nodash(t):
    """Imported text keeps its wording, but em and en dashes become plain punctuation."""
    t = re.sub(r"(\d)\s*[\u2013\u2014]\s*(\d)", r"\1 to \2", t)
    return re.sub(r"\s*[\u2013\u2014]\s*", ", ", t)


for _p in POSTS:
    for _k in ("title", "seo_title", "description"):
        _p[_k] = nodash(_p[_k])
OLD_CASES = {"abu-dhabi-islamic-bank": "adib", "d360-bank": "d360", "national-bank-of-fujairah": "nbf", "beyon-money": "beyon-money", "alaan-pay": "alaan"}


def rooted(doc, root):
    """Move a page one or two folders down: prefix local links and replace the '@/' site-root mark."""
    doc = re.sub(r'((?:href|src)=")(?!https?:|#|mailto:|tel:|/|@/|data:)([^"]+")', lambda m: m.group(1) + root + m.group(2), doc)
    return doc.replace('"@/', '"' + root)


def nice_date(iso):
    d = _date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def post_body(p):
    b = p["body"].replace("\u200d", "")
    b = re.sub(r"(\d)\s*[\u2013\u2014]\s*(\d)", r"\1 to \2", b)   # number ranges
    b = re.sub(r"\s*[\u2013\u2014]\s*", ", ", b)                 # em and en dashes in sentences
    b = re.sub(r"<(p|li)>(?:\s|<br>)+", r"<\1>", b)            # line breaks at the start of a block
    b = re.sub(r"(?:\s|<br>)+</(p|li)>", r"</\1>", b)          # and at the end
    return re.sub(r"<(p|li|h\d)>\s*</\1>", "", b)


def post_card(p):
    img = f'<img src="@/img/blog/{p["cover"]}" alt="" loading="lazy">' if p["cover"] else ""
    return (f'<a class="postcard" href="@/blog/{p["slug"]}/">{img}<span class="postcard__date">{nice_date(p["date"])}</span>'
            f'<b>{e(p["title"])}</b><span>{e(p["description"])}</span></a>')


def head_tags(url, title, desc, image="", article=None):
    t = [f'<link rel="canonical" href="{url}">', f'<meta property="og:title" content="{e(title)}">',
         f'<meta property="og:description" content="{e(desc)}">', f'<meta property="og:url" content="{url}">',
         f'<meta property="og:type" content="{"article" if article else "website"}">']
    if image:
        t.append(f'<meta property="og:image" content="{LIVE}/img/blog/{image}">')
    if article:
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": article["title"], "description": article["description"],
              "datePublished": article["date"], "mainEntityOfPage": url, "publisher": {"@type": "Organization", "name": "Lune"}}
        if image:
            ld["image"] = f"{LIVE}/img/blog/{image}"
        t.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>")
    return "\n".join(t)


def blog_page(root, slug_for_nav, title, desc, body, head):
    doc = page(slug_for_nav, title, desc, body).replace("</head>", head + "\n</head>", 1)
    return rooted(doc, root)


def build_blog():
    n = 0
    index = f"""<section class="hero"><div class="wrap"><div class="hero__copy"><h1 class="h1--page">Lune blog</h1>
<p class="lead">Articles on transaction enrichment, digital banking and Lune news.</p></div></div></section>
<section class="sec sec--white"><div class="wrap"><div class="postgrid">{"".join(post_card(p) for p in POSTS)}</div></div></section>
{cta("See what your card transactions can earn.", "Contact sales for a live demo. We show Lune on sample data, then on a sample of your own transactions.")}"""
    (ROOT / "blog").mkdir(exist_ok=True)
    (ROOT / "blog" / "index.html").write_text(blog_page("../", "blog/", "Lune Blog | Insights on Financial Data Enrichment & Fintech Trends",
        "Stay updated with Lune's latest articles on financial data enrichment, fintech innovations, and industry best practices.", index,
        head_tags(f"{LIVE}/blog", "Lune Blog", "Articles on financial data enrichment, fintech and digital banking.")), encoding="utf-8")
    for k, p in enumerate(POSTS):
        more = [q for q in POSTS if q["slug"] != p["slug"]][k % 5:][:3]
        cover = f'<img class="post__cover" src="@/img/blog/{p["cover"]}" alt="">' if p["cover"] else ""
        body = f"""<article class="post"><div class="wrap post__in">
<a class="more post__back" href="@/blog/">← All articles</a>
<h1 class="h1--page">{e(p["title"])}</h1><p class="lead">{e(p["description"])}</p>
<p class="post__date">Published on <time datetime="{p["date"]}">{nice_date(p["date"])}</time></p>
{cover}
<div class="post__body">{post_body(p)}</div>
</div></article>
<section class="sec sec--white"><div class="wrap stack"><div class="head"><h2>More from the blog</h2></div><div class="postgrid">{"".join(post_card(q) for q in more)}</div></div></section>
{cta("See what your card transactions can earn.", "Contact sales for a live demo. We show Lune on sample data, then on a sample of your own transactions.")}"""
        d = ROOT / "blog" / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(blog_page("../../", "blog/", p["seo_title"], p["description"], body,
            head_tags(f"{LIVE}/blog/{p['slug']}", p["title"], p["description"], p["cover"], p)), encoding="utf-8")
        n += 1
    # Legal pages from the old site, word for word, at their old addresses.
    legal = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "content" / "legal").glob("*.json"))]
    for p in legal:
        body = f"""<article class="post post--legal"><div class="wrap post__in">
<h1 class="h1--page">{e(p["title"])}</h1>
<div class="post__body">{post_body(p)}</div></div></article>"""
        d = ROOT / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(blog_page("../", p["slug"] + "/", p["seo_title"], p["description"], body,
            head_tags(f"{LIVE}/{p['slug']}", p["title"], p["description"])), encoding="utf-8")
    # Other old addresses forward to the closest page on the new site.
    for old, to in [("products/enrich", "enrich.html"), ("products/pulse", "pulse.html"), ("products/engage", "index.html"),
                    ("products/target", "index.html"), ("industries/retail-banks", "index.html"), ("industries/neo-banks-telco-wallets", "index.html"),
                    ("industries/fintechs", "index.html"), ("about", "index.html"), ("careers", "contact.html"), ("contact", "contact.html")]:
        d = ROOT / old
        d.mkdir(parents=True, exist_ok=True)
        up = "../" * (old.count("/") + 1)
        (d / "index.html").write_text(f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><title>Lune</title>'
            f'<link rel="canonical" href="{LIVE}/{to}"><meta http-equiv="refresh" content="0; url={up}{to}"></head>'
            f'<body><p><a href="{up}{to}">Continue to Lune</a></p></body></html>\n', encoding="utf-8")
    # 404 page. Hosts serve it at any depth, so a base tag keeps its links and styles working.
    cards = "".join(map_step(i, st) for i, st in enumerate(STEPS))
    for a, b in [("#enrich", "enrich.html"), ("#analytics", "analytics.html"), ("#in-app", "expenses.html"), ("#pulse", "pulse.html")]:
        cards = cards.replace(f'href="{a}"', f'href="{b}"')
    nf = ('<section class="hero"><div class="wrap"><div class="hero__copy"><h1 class="h1--page">This page does not exist.</h1>'
          '<p class="lead">The address may be old or mistyped. These are the Lune products.</p>'
          '<div class="btns"><a class="btn btn--primary" href="index.html">Go to the home page</a></div></div></div></section>'
          + sec('<div class="map">' + cards + "</div>", "sec--white"))
    doc = page("404.html", "Page not found | Lune", "This page does not exist.", nf)
    base = "<script>document.write('<base href=\"' + (location.pathname.indexOf('/website-v2/') === 0 ? '/website-v2/' : '/') + '\">')</script>"
    (ROOT / "404.html").write_text(doc.replace("<head>", "<head>\n" + base, 1), encoding="utf-8")
    # Old case-study addresses forward to the Customers page.
    for old, anchor in list(OLD_CASES.items()) + [("", "")]:
        d = ROOT / "case-studies" / old if old else ROOT / "case-studies"
        d.mkdir(parents=True, exist_ok=True)
        up = "../../" if old else "../"
        to = f"{up}customers.html" + (f"#{anchor}" if anchor else "")
        (d / "index.html").write_text(f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><title>Lune case studies</title>'
            f'<link rel="canonical" href="{LIVE}/customers.html"><meta http-equiv="refresh" content="0; url={to}"></head>'
            f'<body><p><a href="{to}">Lune case studies</a></p></body></html>\n', encoding="utf-8")
    # Sitemap and robots for search engines.
    urls = [f"{LIVE}/" if s == "index.html" else f"{LIVE}/{s}" for s, *_ in PAGES] + [f"{LIVE}/blog"] + [f"{LIVE}/blog/{p['slug']}" for p in POSTS] + [f"{LIVE}/{p['slug']}" for p in legal]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {LIVE}/sitemap.xml\n", encoding="utf-8")
    missing = [m for f in (ROOT / "blog").rglob("index.html") for m in re.findall(r'src="(?:\.\./)+(img/blog/[^"]+)"', f.read_text(encoding="utf-8")) if not (ROOT / m).exists()]
    for m in sorted(set(missing)):
        print(f"  MISSING blog image: {m}")
    return n, len(set(missing))


if __name__ == "__main__":
    bad = 0
    for slug, title, desc, body in PAGES:
        (ROOT / slug).write_text(page(slug, title, desc, body), encoding="utf-8")
        bad += ste_check(slug, body)
        for src in set(re.findall(r'(?:src|href)="((?:img|ds)/[^"]+|[a-z-]+\.(?:html|css|js))(?:#[^"]*)?"', page(slug, title, desc, body))):
            if not (ROOT / src).exists():
                print(f"  MISSING {slug}: {src}"); bad += 1
    posts, gaps = build_blog()     # imported articles keep their original wording, so the STE check does not run on them
    bad += gaps
    print(f"built {len(PAGES)} pages and {posts} blog posts, {bad} issue(s)")
    sys.exit(1 if bad else 0)
