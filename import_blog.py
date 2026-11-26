"""Import the blog posts from the old Lune website (Webflow) into content/blog/*.json and img/blog/.

Run once, or again to refresh:  python3 import_blog.py
The posts keep their old slugs, titles, descriptions and dates, so the old URLs /blog/<slug> stay valid.
build.py reads content/blog/*.json and writes blog/index.html and blog/<slug>/index.html.
"""
import html
import json
import pathlib
import re
import urllib.parse
import urllib.request
from datetime import datetime
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "content" / "blog"
IMG = ROOT / "img" / "blog"
BASE = "https://www.lunedata.io"
UA = {"User-Agent": "Mozilla/5.0 (site migration)"}

KEEP = {"p", "h2", "h3", "h4", "h5", "ul", "ol", "li", "a", "strong", "b", "em", "i", "blockquote", "br", "img",
        "figure", "figcaption", "table", "thead", "tbody", "tr", "th", "td", "sup", "sub"}
VOID = {"br", "img"}
# Old site paths that have a page on the new site.
MAP = {"/contact": "contact.html", "/products/enrich": "enrich.html", "/products/pulse": "pulse.html", "/case-studies": "customers.html",
       "/case-studies/abu-dhabi-islamic-bank": "customers.html#adib", "/case-studies/d360-bank": "customers.html#d360",
       "/case-studies/national-bank-of-fujairah": "customers.html#nbf", "/case-studies/beyon-money": "customers.html#beyon-money",
       "/case-studies/alaan-pay": "customers.html#alaan", "/blog": "blog/", "/": "index.html", "": "index.html"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read()


def link(href):
    """Rewrite a link from the old site. '@/' marks the site root; build.py replaces it with the right prefix."""
    u = urllib.parse.urlparse(href)
    if u.netloc and "lunedata.io" not in u.netloc or u.scheme in ("mailto", "tel"):
        return href
    if u.netloc and u.netloc not in ("www.lunedata.io", "lunedata.io"):
        return href                                   # docs.lunedata.io, sales.lunedata.io and so on
    path = u.path.rstrip("/")
    if path.startswith("/blog/"):
        return "@/blog/" + path.split("/blog/")[1] + "/"
    return "@/" + MAP.get(path, "index.html")


class Clean(HTMLParser):
    def __init__(self, slug):
        super().__init__(convert_charrefs=True)
        self.out, self.slug, self.n, self.skip = [], slug, 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "iframe"):
            if tag == "iframe" and a.get("src"):
                self.out.append(f'<p><a href="{html.escape(a["src"])}" rel="noopener">Open the video</a></p>')
            self.skip += tag != "iframe"
            return
        if self.skip or tag not in KEEP:
            return
        if tag == "a":
            href = link(a.get("href", ""))
            ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
            self.out.append(f'<a href="{html.escape(href)}"{ext}>')
        elif tag == "img":
            src = a.get("src", "")
            if src:
                self.n += 1
                self.out.append(f'<img src="@/img/blog/{fetch_img(src, f"{self.slug}-{self.n}")}" alt="{html.escape(a.get("alt") or "")}" loading="lazy">')
        else:
            self.out.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        elif not self.skip and tag in KEEP and tag not in VOID:
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(html.escape(data, quote=False))


def fetch_img(src, name):
    ext = pathlib.Path(urllib.parse.urlparse(src).path).suffix.lower() or ".png"
    f = IMG / (name + ext)
    if not f.exists():
        try:
            f.write_bytes(get(src))
        except Exception as err:                       # keep the import going; report the gap
            print(f"  image failed: {src} ({err})")
            return ""
    return f.name


def meta(s, key):
    m = re.search(rf'<meta content="([^"]*)" (?:name|property)="{key}"', s)
    return html.unescape(m.group(1)) if m else ""


def post(slug):
    s = get(f"{BASE}/blog/{slug}").decode("utf-8")
    title = html.unescape(re.search(r'class="h1-100">(.*?)</h1>', s, re.S).group(1)).strip()
    d = re.search(r"Published on</div><div>([^<]+)</div>", s)
    date = datetime.strptime(d.group(1).strip(), "%B %d, %Y").date().isoformat() if d else ""
    i = s.index('class="blog-body-rich w-richtext">') + len('class="blog-body-rich w-richtext">')
    j = s.index("</section>", i)
    raw = s[i:j]
    raw = raw[:raw.rindex("</div>")]                  # close of the rich text block and its wrappers
    c = Clean(slug)
    c.feed(raw)
    body = "".join(c.out)
    body = re.sub(r"<(p|h\d|li|strong|em|b|i)>\s*(?:<br>)?\s*</\1>", "", body)   # empty blocks
    body = re.sub(r"<p>‍</p>", "", body)
    cover = meta(s, "og:image")
    return {"slug": slug, "title": title, "seo_title": html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1)).strip(),
            "description": meta(s, "description"), "date": date, "cover": fetch_img(cover, slug + "-cover") if cover else "", "body": body}


LEGAL = ["terms", "lune-privacy", "cookie", "msa", "msa-secan"]


def legal(slug):
    """A legal page from the old site. The text stays word for word."""
    s = get(f"{BASE}/{slug}").decode("utf-8")
    m = re.search(r'class="[^"]*w-richtext[^"]*">', s)
    raw = s[m.end():s.index("</section>", m.end())]
    raw = raw[:raw.rindex("</div>")]
    c = Clean("legal-" + slug)
    c.feed(raw)
    body = re.sub(r"<(p|h\d|li|strong|em|b|i)>\s*(?:<br>)?\s*</\1>", "", "".join(c.out))
    h1 = re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1)).strip()
    return {"slug": slug, "title": html.unescape(h1), "seo_title": html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1)).strip(),
            "description": meta(s, "description"), "body": body}


if __name__ == "__main__":
    (ROOT / "content" / "legal").mkdir(parents=True, exist_ok=True)
    for slug in LEGAL:
        p = legal(slug)
        (ROOT / "content" / "legal" / f"{slug}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"legal       {len(p['body']):6}  {slug}  ({p['title']})")
    OUT.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    index = get(BASE + "/sitemap.xml").decode("utf-8")
    slugs = sorted(set(re.findall(r"<loc>https://www\.lunedata\.io/blog/([^<]+)</loc>", index)))
    for slug in slugs:
        try:
            p = post(slug)
        except Exception as err:
            print(f"  FAILED {slug}: {err}")
            continue
        (OUT / f"{slug}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{p['date'] or 'no date':10}  {len(p['body']):6}  {slug}")
    print(f"{len(list(OUT.glob('*.json')))} posts in {OUT}")
