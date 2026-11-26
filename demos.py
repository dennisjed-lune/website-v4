"""Animated product demos and home hero options for the Lune site.

Each demo has two animation options (data-v="1" and data-v="2"). site.js shows one option and runs it in steps:
it adds the classes s1, s2, s3 to the .dv element, one for each duration in data-steps. The CSS does the motion.
Content rules are the same as mocks.py: sample data only, no city, cryptic raw text, offer merchants from the sheet.
"""
import html
from mocks import BRANDS, ENRICH_TX, LOGO

e = html.escape
CAP = ""   # one sample-data note sits in the page footer


def dv(cls, steps, inner, label, hook=""):
    h = f' data-hook="{hook}"' if hook else ""
    return f'<div class="ui-wrap"><div class="dv {cls}" data-steps="{steps}"{h} role="img" aria-label="{e(label)}">{inner}</div></div>'


def demo(name, *opts, cls=""):
    """Each option is (label pill, dv html, caption). Two options get the review toggle. One option has no toggle."""
    out = ""
    for i, (label, body, cap) in enumerate(opts, 1):
        hidden = "" if i == 1 else " hidden"
        out += (f'<div class="demo__v" data-v="{i}"{hidden}><div class="shot__frame">{body}</div>'
                + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</div>')
    return f'<figure class="shot demo {cls}" data-demo="{name}" data-parallax="0.05">{out}</figure>'


# ------------------------------------------------------------------ ENRICH
DECODE = f'''<div class="ui dc">
<div class="dc__in"><span class="dc__lab">From your bank</span><code data-f="raw" data-type>POS PUR 448812 LVL SHS DXB MALL 00AE</code><i class="dc__scan"></i></div>
<div class="dc__via"><i></i><span>Enrich</span></div>
<div class="dc__out">
<div class="dc__f dc__f--1 ui__key"><span class="dc__lab">Merchant and logo</span><span class="ui__brand"><img data-f="logo" src="{LOGO}levelshoes.png" alt=""><b data-f="merchant">Level Shoes</b></span></div>
<div class="dc__f dc__f--2"><span class="dc__lab">Category</span><b data-f="cat">Shopping › Clothing</b></div>
<div class="dc__f dc__f--3"><span class="dc__lab">Recurring</span><b data-f="rec">No</b></div>
</div><p class="ui__note">Enrich names the merchant behind each card description.</p></div>'''

ENRICH_DEMO = demo("enrich",
    ("Enrich API · One transaction", dv("dv-decode", "900,1000,800,700,2600", DECODE, "One card description becomes a merchant, a logo and a category", "tx"), CAP))

# ------------------------------------------------------------------ ANALYTICS
CALLOUT = '<div class="callout"><span>Most customers</span><b>Carrefour · 188,410</b></div>'
FILL = dv("dv-fill", "500,4600", ENRICH_TX.replace("Enrich names the merchant behind each card description.", "LuneHub lists each transaction with its enriched result."),
          "LuneHub transactions list. Each card description gets a merchant and a category")
BARS = dv("dv-bars", "500,1700,1400,3400", BRANDS + CALLOUT, "Brand explorer. Bars show spend for each brand, then the number of customers")

LUNEHUB_DEMO = demo("lunehub", ("LuneHub · Transactions", FILL, CAP))        # home, step 02
ANALYTICS_DEMO = demo("analytics", ("LuneHub · Analytics · Brands", BARS, CAP))  # Analytics page

# ------------------------------------------------------------------ EXPENSES AND CASHFLOW (mobile SDK)
# A phone in a device frame on a stage. Cards pop out at the sides, one for each step.
def svg(path):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'


ICON = {
    "line": svg('<path d="M3 17l5-5 4 3 8-9"/><path d="M3 21h18"/>'),
    "pie": svg('<path d="M12 3a9 9 0 1 0 9 9h-9z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z"/>'),
    "store": svg('<path d="M4 9l1.5-5h13L20 9"/><path d="M4 9v11h16V9"/><path d="M9 20v-6h6v6"/>'),
    "target": svg('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/>'),
    "in": svg('<path d="M17 7L7 17"/><path d="M7 9v8h8"/>'),
    "clock": svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    "chat": svg('<path d="M4 5h16v11H9l-5 4z"/>'),
    "flag": svg('<path d="M5 21V4"/><path d="M5 4h12l-2 4 2 4H5"/>'),
    "bulb": svg('<path d="M9 18h6"/><path d="M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.4 1 1.1 1 1.8V16h5v-.3c0-.7.4-1.4 1-1.8A6 6 0 0 0 12 3z"/>'),
}


def pop(pos, at, icon, title, text, ring=None):
    lead = f'<span class="ring" style="--v:{ring}"></span>' if ring else f'<span class="pop__i">{ICON[icon]}</span>'
    return f'<div class="pop pop--{pos} at{at}">{lead}<span><b>{title}</b><i>{text}</i></span></div>'


def unit(name, cap, screen, pops, shot=False):
    kind = " dev--shot" if shot else ""
    return (f'<div class="unit"><div class="dev{kind}"><div class="dev__scr">{screen}</div></div>{"".join(pops)}'
            '</div>')   # no name or caption under the phone


def stage(word, units, steps, label, pair=False):
    return dv("stage" + (" stage--pair" if pair else ""), steps, units, label)


TAP_ROW = '<span class="tap tap--row"></span>'


def row(logo, name, sub, amt, at, tap=False):
    return f'<div class="app__row{f" fx at{at}" if at else ""}{" is-tapped" if tap else ""}"><img src="{LOGO}{logo}" alt=""><span><b>{name}</b><i>{sub}</i></span><em>{amt}</em>{TAP_ROW if tap else ""}</div>'


def bar_row(name, amt, w, g, cls=""):
    return f'<div class="app__bar"><span>{name}</span><em>{amt}</em><u class="grow g{g} {cls}" style="--w:{w}%"></u></div>'


TIME = '<span class="app__time">9:41</span>'


def row_l(letter, name, sub, amt, at=1):
    return f'<div class="app__row fx at{at}"><span class="app__av">{letter}</span><span><b>{name}</b><i>{sub}</i></span><em>{amt}</em></div>'


def kv_row(k, v):
    return f'<div class="app__bar"><span>{k}</span><em>{v}</em></div>'


# Expenses, option 1: real SDK screens. Each screen brings one card.
EXP_SCREENS = ('<img src="img/app/exp-home.png" alt="" loading="lazy"><img src="img/app/exp-cats.png" alt="" loading="lazy">'
               '<img src="img/app/exp-brands.png" alt="" loading="lazy"><span class="tap tap--shot"></span>')
EXP_REAL_POPS = [pop("l1", 1, "line", "Day by day", "This month against last month"), pop("r2", 2, "pie", "Category trends", "Spend and share of spend"),
                 pop("l3", 3, "store", "Brand trends", "Spend for each day and top brands")]

# Expenses, option 2: a drawn screen. The chart draws, the split grows, a tap opens one payment.
EXP_APP = f"""<div class="app">{TIME}
<div class="app__top"><b>Expenses</b><span class="app__pill">November</span></div>
<span class="app__k">Spent so far</span><b class="app__big" data-count="6808" data-pre="AED " data-at="1">AED 6,808</b>
<span class="app__good">AED 187 less than last month</span>
<div class="app__card ex__card"><svg class="ex__chart" viewBox="0 0 240 86" preserveAspectRatio="none" aria-hidden="true">
<path class="ex__last" d="M0 80 C40 70,80 52,120 40 S200 18,240 10"/><path class="ex__area" d="M0 80 C30 74,50 60,80 56 S120 40,150 34 L150 86 L0 86Z"/>
<path class="ex__line" pathLength="1" d="M0 80 C30 74,50 60,80 56 S120 40,150 34"/></svg><i class="ex__dot"></i>
<div class="ex__axis"><span>1 Nov</span><span>Today</span><span>30 Nov</span></div></div>
<span class="app__h">Where it went</span>
<div class="ex__split"><i style="--w:24%;--c:var(--cat-grocery)"></i><i style="--w:22%;--c:var(--cat-shopping)"></i><i style="--w:18%;--c:var(--cat-dining)"></i><i style="--w:14%;--c:var(--cat-travel)"></i><i style="--w:22%;--c:#C9CED4"></i></div>
<div class="ex__rows">{row("carrefour.png", "Carrefour", "Groceries", "AED 412.30", 0, tap=True)}{row("starbucks.png", "Starbucks", "Dining", "AED 24.00", 0)}{row("netflix.png", "Netflix", "Entertainment", "AED 56.99", 0)}</div>
<span class="scrim"></span>
<div class="sheet"><i class="sheet__grip"></i><img src="{LOGO}carrefour.png" alt=""><b>Carrefour</b><span>Groceries › Supermarket</span><b class="sheet__amt">AED 412.30</b>
<div class="sheet__tags"><i>Work</i><i>Family</i><i>Add a tag</i></div><span class="sheet__fb">Wrong merchant or category? Report it</span></div>
</div>"""
EXP_DRAWN_POPS = [pop("l2", 2, "target", "Groceries budget", "AED 1,640 of AED 2,250", ring=73), pop("r1", 3, "store", "Top brand", "Carrefour · AED 1,240"),
                  pop("r3", 5, "flag", "Customer feedback", "Report a wrong merchant")]

# Cashflow, option 1: the home screen after the customer selects the salary day.
CF_HOME = f"""<div class="app">{TIME}
<div class="app__top"><b>Cashflow</b><span class="app__pill">25 Oct to 24 Nov</span></div>
<span class="app__chip">Your month starts on the 25th</span>
<span class="app__k">Total cashflow</span><b class="app__big" data-count="6600" data-pre="+AED " data-at="1">+AED 6,600</b>
<span class="app__good">AED 420 better than last month</span>
<div class="app__card">{bar_row("Money in", "AED 18,500", 100, 1)}{bar_row("Money out", "AED 11,900", 64, 1, "out")}</div>
<span class="app__h fx at2">Money in</span>
<div class="app__card fx at2">{bar_row("Income", "AED 16,000", 86, 2)}{bar_row("Transfers in", "AED 2,100", 11, 2)}{bar_row("Government services", "AED 400", 3, 2)}</div>
<span class="app__h fx at3">Money out</span>
<div class="app__card fx at3">{bar_row("Card spend", "AED 4,800", 40, 3, "out")}{bar_row("Bills", "AED 3,900", 33, 3, "out")}{bar_row("Transfers out", "AED 3,200", 27, 3, "out")}</div>
<div class="app__card cf__note fx at4"><span class="app__k">Cashflow summary</span><p>You kept AED 6,600 this month. That is 36% of money in.</p></div>
</div>"""
CF_HOME_POPS = [pop("l1", 2, "in", "Salary arrived", "25 Oct · AED 16,000"), pop("r3", 4, "pie", "You kept 36%", "of money in this month", ring=36)]

# Cashflow, option 2: six months of history, then one month and its summary.
TREND = [("Jun", 70, 58), ("Jul", 74, 66), ("Aug", 68, 71), ("Sep", 80, 60), ("Oct", 77, 63), ("Nov", 92, 59)]
TREND_BARS = "".join(f'<div style="--a:{a}%;--b:{b}%"><u><i class="grow-y"></i><i class="grow-y out"></i></u><span>{m}</span></div>' for m, a, b in TREND)
CF_TREND = f"""<div class="app">{TIME}
<div class="app__top"><b>Cashflow</b><span class="app__pill">Trends</span></div>
<div class="app__tabs"><i class="is-on">Total</i><i>Money in</i><i>Money out</i></div>
<div class="app__card"><div class="tb">{TREND_BARS}</div>
<div class="tb__key"><span><i></i>Money in</span><span><i class="out"></i>Money out</span></div></div>
<div class="app__card cf__month fx at2"><span class="app__k">November</span><b class="app__big" data-count="6600" data-pre="+AED " data-at="2">+AED 6,600</b>
<div class="cf__pair"><span>Money in<b>AED 18,500</b></span><span>Money out<b>AED 11,900</b></span></div></div>
<div class="app__card cf__note fx at3"><span class="app__k">Cashflow summary</span><p>You kept AED 6,600 this month. That is 36% of money in.</p></div>
<span class="app__h fx at3">History</span>
<div class="app__card fx at3"><div class="app__bar"><span>October</span><em>+AED 4,900</em></div><div class="app__bar"><span>September</span><em>+AED 6,100</em></div><div class="app__bar"><span>August</span><em>AED 1,050 short</em></div><div class="app__bar"><span>July</span><em>+AED 2,750</em></div><div class="app__bar"><span>June</span><em>+AED 3,900</em></div></div>
<span class="tap tap--bar"></span>
</div>"""
CF_TREND_POPS = [pop("l1", 1, "clock", "Six months of history", "Money in against money out"), pop("r3", 3, "bulb", "Smart insight", "In plain language")]

# Still screens for the product pages. Each one fills the phone.
CF_IN = f"""<div class="app">{TIME}
<div class="app__top"><b>Money in</b><span class="app__pill">25 Oct to 24 Nov</span></div>
<span class="app__k">4 sources · 5 transactions</span><b class="app__big">AED 18,500</b>
<div class="ex__split"><i style="--w:86%;--c:var(--lune-emerald)"></i><i style="--w:11%;--c:var(--lune-teal-700)"></i><i style="--w:3%;--c:var(--lune-sea)"></i></div>
<div class="app__card">{kv_row("Income", "86% · AED 16,000")}{kv_row("Transfers in", "11% · AED 2,100")}{kv_row("Government services", "3% · AED 400")}</div>
<div class="app__tabs app__tabs--2"><i class="is-on">Sources</i><i>Transactions</i></div>
<div class="ex__rows">{row_l("E", "Employer salary", "Income · 1 transaction", "AED 16,000")}{row_l("S", "Sara Khan", "Transfers in · 2 transactions", "AED 1,436")}{row_l("O", "Own savings account", "Transfers in · 1 transaction", "AED 664")}{row_l("H", "Housing support", "Government services · 1 transaction", "AED 400")}</div>
<div class="app__card cf__note"><span class="app__k">Insight</span><p>Income is 86% of money in this month.</p></div>
</div>"""

EX_TX = f"""<div class="app">{TIME}
<div class="app__top"><b>Payment</b><span class="app__pill">Thu 12 Nov</span></div>
<div class="app__hero"><img src="{LOGO}starbucks.png" alt=""><b>Starbucks</b><b class="app__big">AED 24.00</b><span>Card payment · 08:53</span></div>
<div class="app__card">{kv_row("Category", "Dining › Coffeeshop")}{kv_row("Card", "Gold credit")}{kv_row("Recurring", "No")}</div>
<span class="app__h">Tags</span><div class="sheet__tags app__tags"><i>Work</i><i>Family</i><i>Add a tag</i></div>
<span class="app__h">More from Starbucks</span>
<div class="app__card">{kv_row("Thu 5 Nov", "AED 22.00")}{kv_row("Thu 29 Oct", "AED 31.50")}{kv_row("Wed 21 Oct", "AED 24.00")}</div>
<span class="app__link">Wrong merchant or category? Report it</span>
</div>"""

BRAND_BARS = "".join(f'<div style="--a:{a}%"><u><i class="grow-y"></i></u><span>{m}</span></div>' for m, a in [("Jun", 62), ("Jul", 70), ("Aug", 48), ("Sep", 81), ("Oct", 74), ("Nov", 92)])
EX_BRAND = f"""<div class="app">{TIME}
<div class="app__top"><b>Carrefour</b><span class="app__pill">Groceries</span></div>
<span class="app__k">Spent so far this month</span><b class="app__big">AED 1,240</b>
<span class="app__good app__good--flat">AED 96 more than last month by today</span>
<div class="app__card"><div class="tb">{BRAND_BARS}</div><div class="tb__key"><span><i></i>Spend for each month</span></div></div>
<span class="app__h">Payments this month</span>
<div class="app__card">{kv_row("Thu 12 Nov", "AED 412.30")}{kv_row("Fri 6 Nov", "AED 356.20")}{kv_row("Sun 1 Nov", "AED 471.50")}</div>
<span class="app__h">Last month</span>
<div class="app__card">{kv_row("Sat 24 Oct", "AED 388.40")}{kv_row("Thu 15 Oct", "AED 402.10")}{kv_row("Sat 3 Oct", "AED 353.50")}</div>
<div class="app__card">{kv_row("Average for a month", "AED 1,090")}{kv_row("Share of Groceries", "76%")}</div>
</div>"""


def phone_drawn(screen, title, text):
    """A still, drawn SDK screen in a device frame, for the product pages."""
    return (f'<figure class="phone"><div class="dv" data-steps="1,1,1,1,1,1" data-static role="img" aria-label="{e(title)} screen">'
            f'<div class="dev"><div class="dev__scr">{screen}</div></div></div><figcaption><b>{title}</b><span>{text}</span></figcaption></figure>')


SHOT_CAP = "Screens from the Lune SDK with sample data."
DRAWN_CAP = ""
PILL = "Lune SDK · iOS and Android"


# AI assistant: a question, an answer from enriched data, then a Pulse offer that matches the spend.
CHAT = f"""<div class="app chat">{TIME}
<div class="app__top"><b>Assistant</b><span class="app__pill">Expenses</span></div>
<p class="chat__me fx at1">How much did I spend on shopping this month?</p>
<div class="chat__bot fx at2"><p>You spent <b>AED 1,840</b> on shopping this month. Your top merchants are Level Shoes and IKEA.</p>
<div class="chat__row"><img src="{LOGO}levelshoes.png" alt=""><span><b>Level Shoes</b><i>Shopping › Clothing</i></span><em>AED 1,032.00</em></div>
<div class="chat__row"><img src="{LOGO}ikea.png" alt=""><span><b>IKEA</b><i>Shopping › Furniture</i></span><em>AED 645.00</em></div></div>
<div class="chat__bot chat__offer fx at3"><span class="chat__tag">Offer for you</span>
<div class="chat__row"><img src="{LOGO}levelshoes.png" alt=""><span><b>10% cashback</b><i>At Level Shoes, with your card</i></span></div>
<span class="chat__btn"><i>Activate offer</i><i>Offer activated</i><span class="tap tap--btn"></span></span></div>
<p class="chat__bot chat__done fx at4">Done. Pay with your card at Level Shoes to earn the cashback.</p>
<div class="chat__chips"><i>Top merchants</i><i>Compare months</i><i>Offers for me</i></div>
<div class="chat__input"><span>Ask about your spending</span><u></u></div>
</div>"""
CHAT_POPS = [pop("l2", 2, "chat", "Answer from your data", "Real merchant names"), pop("r3", 3, "store", "Pulse offer", "Matches shopping spend")]
AI_DEMO = demo("ai", ("Assistant in the Lune SDK", stage("Assistant", unit("Assistant", "A question, an answer and an offer", CHAT, CHAT_POPS), "700,1500,3000,2600,4400",
                      "A customer asks about shopping spend. The assistant answers and shows a cashback offer from the top merchant"), ""), cls="demo--phones")


def crow(logo, name, sub, amt=""):
    em = f"<em>{amt}</em>" if amt else ""
    return f'<div class="chat__row"><img src="{LOGO}{logo}" alt=""><span><b>{name}</b><i>{sub}</i></span>{em}</div>'


def snip(q, answer):
    return f'<div class="snip"><div class="snip__scr chat" role="img" aria-label="{e(q)}"><p class="chat__me">{q}</p>{answer}</div></div>'


# Four still question-and-answer examples for the AI page. Amounts agree with the Expenses screens.
SNIPS = "".join([
    snip("How much did I spend on shopping this month?",
         '<div class="chat__bot"><p>You spent <b>AED 1,840</b> on shopping this month.</p>' + crow("levelshoes.png", "Level Shoes", "Shopping › Clothing", "AED 1,032.00") + crow("ikea.png", "IKEA", "Shopping › Furniture", "AED 645.00") + "</div>"),
    snip("Where do I spend the most?",
         '<div class="chat__bot"><p>Your top three merchants this month:</p>' + crow("carrefour.png", "Carrefour", "Groceries › Supermarket", "AED 1,240.00") + crow("levelshoes.png", "Level Shoes", "Shopping › Clothing", "AED 1,032.00") + crow("ikea.png", "IKEA", "Shopping › Furniture", "AED 645.00") + "</div>"),
    snip("Did I spend more than last month?",
         '<div class="chat__bot"><p>No. You spent <b>AED 6,808</b> so far this month. That is <b>AED 187 less</b> than last month.</p>'
         '<div class="chat__cmp"><span>This month<u style="--w:97%"></u><em>AED 6,808</em></span><span>Last month<u class="was" style="--w:100%"></u><em>AED 6,995</em></span></div></div>'),
    snip("Are there offers for me?",
         '<div class="chat__bot"><p>Yes. You spent <b>AED 1,032</b> at Level Shoes this month.</p></div>'
         '<div class="chat__bot chat__offer"><span class="chat__tag">Offer for you</span>' + crow("levelshoes.png", "10% cashback", "At Level Shoes, with your card") + '<span class="chat__btn"><i>Activate offer</i></span></div>'),
])


def phones_demo(kind):
    """kind: 'both' (home), 'exp' or 'cf'. Two options each, with the review toggle."""
    exp1 = unit("Expenses", "Real merchant names and trends", EXP_SCREENS, EXP_REAL_POPS if kind == "exp" else EXP_REAL_POPS[::2], shot=True)
    exp2 = unit("Expenses", "From the month to one payment", EXP_APP, EXP_DRAWN_POPS if kind == "exp" else EXP_DRAWN_POPS[:1])
    cf1 = unit("Cashflow", "Money in against money out", CF_HOME, CF_HOME_POPS if kind == "cf" else CF_HOME_POPS[1:])
    cf2 = unit("Cashflow", "Six months and a summary", CF_TREND, CF_TREND_POPS if kind == "cf" else CF_TREND_POPS[1:])
    steps1, steps2 = "1400,2600,2600,2600,1200", "700,1600,1500,1500,2200,2600"
    steps_tap = "700,1600,1500,2000,3700,2800"  # the row tap needs a longer fourth step
    # Dennis selected option 2 for both products (26 Nov 2026). Option 1 (exp1, cf1) stays in the code for reference.
    if kind == "exp":
        return demo("sdk-exp", (PILL, stage("Expenses", exp2, steps_tap, "An Expenses screen. A chart, a category split and one payment in detail"), DRAWN_CAP), cls="demo--phones")
    if kind == "cf":
        return demo("sdk-cf", (PILL, stage("Cashflow", cf2, steps2, "Cashflow trends. Six months of history and a summary"), DRAWN_CAP), cls="demo--phones")
    return demo("sdk-both", (PILL, stage("In your app", exp2 + cf2, steps_tap, "Expenses and Cashflow screens in a bank app", pair=True), DRAWN_CAP), cls="demo--phones")


# ------------------------------------------------------------------ PULSE
PULSE_CB = f'''<div class="ui pc">
<div class="pc__pay"><img src="{LOGO}levelshoes.png" alt=""><span><b>Level Shoes</b><i>Card payment · Gold credit</i></span><em>AED 1,032.00</em></div>
<div class="pc__link"><span class="ui__pill ok">Activated offer · 10% cashback</span></div>
<div class="pc__win"><span>Cashback earned</span><b>+AED 103.20</b><small>Funded by Level Shoes</small><u></u><u></u><u></u><u></u><u></u><u></u></div>
<div class="pc__bal ui__key"><span>Cashback this month</span><b data-count="317.80" data-from="214.60" data-dec="2" data-pre="AED " data-at="4">AED 317.80</b></div>
<p class="ui__note">The customer earns when a card payment matches an activated offer.</p></div>'''

PULSE_TIER = '''<div class="ui pt">
<div class="pt__top"><div class="pt__tier"><span>Your tier</span><b class="pt__names"><i>Gold</i><i>Platinum</i></b></div>
<span class="ui__pill pt__rate"><i>1.5× points</i><i>2× points</i></span></div>
<div class="pt__track"><i></i></div>
<div class="pt__nums"><span><b data-count="40000" data-from="33800" data-at="1">40,000</b> of 40,000 points</span><span class="ui__pill ok pt__up">Platinum tier reached</span></div>
<div class="pt__mission"><div><b>Mission: five purchases this month</b><span>Bonus reward for repeat spend</span></div>
<div class="pt__dots"><i></i><i></i><i></i><i></i><i></i></div><span class="ui__pill ok pt__done">Mission complete</span></div>
<p class="ui__note">Customers earn more at each tier. Missions reward repeat spend.</p></div>'''

APP_CAP = ""
PULSE_DEMO = demo("pulse",
    ("Customer app · Cashback", dv("dv-cash", "700,1000,1000,1100,1300,3000", PULSE_CB, "A card payment at Level Shoes earns AED 103.20 cashback, funded by the merchant"), APP_CAP))
TIER_DEMO = demo("pulse-tier",
    ("Customer app · Tiers and missions", dv("dv-tier", "700,1700,1200,1500,900,3000", PULSE_TIER, "A customer reaches the Platinum tier and completes a mission"), APP_CAP))

# ------------------------------------------------------------------ HOME HERO OPTIONS
DRIFT = ["POS PUR 448812 LVL SHS 00AE", "MAF HYPMKT MOE-0042 ARE", "NF* 8665797172 00012", "ALSHAYA SBX 0921 GT AE", "UBR* PENDING 4029357733",
         "FZ 1418829 T2 AE 784", "AMZ*MKTPL SA 2K4LP0 682", "EXP*72619940183 ECOM 840", "RBK 3307 CC TID88120", "SPTF AB P2A91F 752"]


def drift(n, seed=0):
    """Raw card descriptions that move at different speeds behind a section. Rows are spaced so that no two overlap."""
    out = ""
    for i in range(n):
        k = (i * 7 + seed) % len(DRIFT)
        x, y = (i * 41 + seed * 11) % 80, 4 + i * (88 // n)
        sp = 0.06 + ((i * 5 + seed) % 6) * 0.035
        out += f'<span class="drift" data-parallax="{sp:.3f}" style="left:{x}%;top:{y}%;--o:{0.45 + (i % 3) * 0.25:.2f}">{e(DRIFT[k])}</span>'
    return f'<div class="sec__bg" aria-hidden="true">{out}</div>'


DECODER = f'''<div class="decoder dv" data-steps="1000,1000,900,800,2400" data-hook="tx" aria-hidden="true">
<div class="feed__top"><span class="feed__live">Example feed</span><span class="feed__count"><span data-feedcount>1,482,113</span> enriched today</span></div>
<div class="decoder__main">
<div class="decoder__raw"><span class="dc__lab">From your bank</span><code data-f="raw" data-type>POS PUR 448812 LVL SHS DXB MALL 00AE</code><span class="decoder__amt" data-f="amt">AED 1,032.00</span></div>
<div class="decoder__node"><i></i></div>
<div class="decoder__out"><span class="dc__lab">Enriched by Lune</span>
<div class="decoder__who"><img data-f="logo" src="{LOGO}levelshoes.png" alt=""><div><b data-f="merchant">Level Shoes</b><span data-f="cat">Shopping › Clothing</span></div></div>
<span class="tx__offer" data-f="offer">10% cashback</span></div>
</div>
<div class="trail"></div>
</div>'''

SCENE = f'''<div class="scene dv" data-steps="700,1000,800,800,800,2600" data-hook="tx" aria-hidden="true">
<div class="scene__rings"><i></i><i></i><i></i></div>
<div class="scene__tilt">
<div class="bankcard bankcard--c"></div><div class="bankcard bankcard--b"></div>
<div class="bankcard"><span class="bankcard__brand"><i></i>Your bank</span><span class="bankcard__chip"></span><span class="bankcard__no">Gold credit</span><span class="bankcard__tap"></span></div>
<div class="fl fl--raw"><span class="dc__lab">From your bank</span><code data-f="raw">POS PUR 448812 LVL SHS DXB MALL 00AE</code></div>
<div class="fl fl--who"><img data-f="logo" src="{LOGO}levelshoes.png" alt=""><div><b data-f="merchant">Level Shoes</b><span data-f="cat">Shopping › Clothing</span></div></div>
<div class="fl fl--amt"><span class="dc__lab">Amount</span><b data-f="amt">AED 1,032.00</b></div>
<div class="fl fl--bars"><span class="dc__lab">Spend by category</span><u style="--w:100%"></u><u style="--w:74%"></u><u style="--w:52%"></u><u style="--w:31%"></u></div>
<div class="fl fl--offer"><span class="tx__offer" data-f="offer">10% cashback</span></div>
</div></div>'''

JOURNEY = f'''<div class="journey dv" data-steps="900,1300,1300,1300,1300,2800" data-hook="tx" data-only="offer" aria-hidden="true">
<div class="journey__line"><i></i></div>
<div class="jn jn--0"><span class="jn__k">Card payment</span><code data-f="raw">POS PUR 448812 LVL SHS DXB MALL 00AE</code><span data-f="amt">AED 1,032.00</span></div>
<div class="jn jn--1"><span class="jn__k">Enrich</span><div class="jn__who"><img data-f="logo" src="{LOGO}levelshoes.png" alt=""><div><b data-f="merchant">Level Shoes</b><span data-f="cat">Shopping › Clothing</span></div></div></div>
<div class="jn jn--2"><span class="jn__k">Analytics</span><div class="jn__bars"><u style="--w:100%"></u><u style="--w:72%"></u><u style="--w:46%"></u></div><span class="jn__s">Spend by brand, in LuneHub</span></div>
<div class="jn jn--3"><span class="jn__k">PFM</span><div class="jn__who"><img data-f="logo" src="{LOGO}levelshoes.png" alt=""><div><b data-f="merchant">Level Shoes</b><span data-f="amt">AED 1,032.00</span></div></div><span class="jn__s">A clear name in your app</span></div>
<div class="jn jn--4"><span class="jn__k">Pulse</span><b class="jn__big" data-f="offer">10% cashback</b><span class="jn__s">Funded by the merchant</span></div>
</div>'''
