"""Builds the WordPress inner pages from the home page's theme shell.

Run once when the content changes; the generated files are committed, so the
fixture's bytes never depend on this script at run time.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "site" / "wordpress"
home = (ROOT / "index.html").read_text()

head_end = home.index("<body ")
body_start = home.index('<div class="entry-content clear"')
body_end = home.index("</article>")

PAGES = {
    "services": {
        "id": 9,
        "title": "Services &amp; Prices | Copperleaf Cycle Works",
        "desc": "Bike repair services and prices at Copperleaf Cycle Works in Marrow Falls.",
        "crumb": "Services",
        "content": """
<h1 class="wp-block-heading">Services</h1>
<p>Every job starts with a free safety check. Prices include labor; parts are extra unless noted.</p>
<figure class="wp-block-table is-style-stripes"><table class="has-fixed-layout"><thead><tr><th>Service</th><th>Price</th></tr></thead><tbody>
<tr><td>Basic tune-up</td><td>$79</td></tr>
<tr><td>Full overhaul</td><td>from $189</td></tr>
<tr><td>Flat tire repair (tube included)</td><td>$15</td></tr>
<tr><td>Wheel truing</td><td>$25 per wheel</td></tr>
<tr><td>Brake service</td><td>$35 per wheel</td></tr>
<tr><td>Bike fitting</td><td>$120</td></tr>
<tr><td>E-bike service</td><td>Call for a quote</td></tr>
</tbody></table></figure>
<p>Most tune-ups are ready within two business days. Need it sooner? Ask about same-day service.</p>
""",
    },
    "about": {
        "id": 11,
        "title": "About Us | Copperleaf Cycle Works",
        "desc": "Copperleaf Cycle Works has kept Marrow Falls riding since 2011.",
        "crumb": "About Us",
        "content": """
<h1 class="wp-block-heading">About Us</h1>
<p>Copperleaf Cycle Works opened in 2011 in a one-bay garage on Tannery Row. Fifteen years later we&rsquo;re still a family shop, just with a bigger bay and more stands.</p>
<p>Our mechanics are certified by the Pacific Bicycle Mechanics Guild, and every repair carries our 30-day guarantee. We work on road, mountain, kids&rsquo; and cargo bikes, and on most e-bikes.</p>
<p>We&rsquo;re proud members of the Linden Valley Chamber of Commerce.</p>
""",
    },
    "contact": {
        "id": 13,
        "title": "Contact | Copperleaf Cycle Works",
        "desc": "Find Copperleaf Cycle Works on Tannery Row in Marrow Falls. Call, email or send us a message.",
        "crumb": "Contact",
        "content": """
<h1 class="wp-block-heading">Contact</h1>
<div class="wp-block-columns is-layout-flex wp-block-columns-is-layout-flex">
<div class="wp-block-column is-layout-flow wp-block-column-is-layout-flow">
<h2 class="wp-block-heading">Visit</h2>
<p>418 Tannery Row, Unit B<br>Marrow Falls, OR 97999</p>
<h2 class="wp-block-heading">Call or email</h2>
<p>Phone: <a href="tel:+15415550142">(541) 555-0142</a><br>Email: <a href="mailto:hello@copperleaf-cycles.example">hello@copperleaf-cycles.example</a></p>
<h2 class="wp-block-heading">Hours</h2>
<figure class="wp-block-table"><table><tbody>
<tr><td>Monday</td><td>Closed</td></tr>
<tr><td>Tuesday &ndash; Friday</td><td>9:30am &ndash; 6pm</td></tr>
<tr><td>Saturday</td><td>9am &ndash; 4pm</td></tr>
<tr><td>Sunday</td><td>Closed</td></tr>
</tbody></table></figure>
<p><em>Holiday hours: closed Thanksgiving Day and December 25.</em></p>
</div>
<div class="wp-block-column is-layout-flow wp-block-column-is-layout-flow">
<h2 class="wp-block-heading">Book a repair</h2>
<div class="wpcf7 no-js" id="wpcf7-f42-p13-o1" lang="en-US" dir="ltr">
<form action="/contact/#wpcf7-f42-p13-o1" method="post" class="wpcf7-form init" aria-label="Contact form" novalidate="novalidate" data-status="init">
<div style="display: none;"><input type="hidden" name="_wpcf7" value="42" /><input type="hidden" name="_wpcf7_version" value="5.9.8" /><input type="hidden" name="_wpcf7_unit_tag" value="wpcf7-f42-p13-o1" /></div>
<p><label> Your name<br /><span class="wpcf7-form-control-wrap" data-name="your-name"><input size="40" maxlength="400" class="wpcf7-form-control wpcf7-text wpcf7-validates-as-required" aria-required="true" value="" type="text" name="your-name" /></span></label></p>
<p><label> Your email<br /><span class="wpcf7-form-control-wrap" data-name="your-email"><input size="40" maxlength="400" class="wpcf7-form-control wpcf7-email wpcf7-validates-as-required wpcf7-text wpcf7-validates-as-email" aria-required="true" value="" type="email" name="your-email" /></span></label></p>
<p><label> What does your bike need?<br /><span class="wpcf7-form-control-wrap" data-name="your-message"><textarea cols="40" rows="10" maxlength="2000" class="wpcf7-form-control wpcf7-textarea" name="your-message"></textarea></span></label></p>
<p><input class="wpcf7-form-control wpcf7-submit has-spinner" type="submit" value="Send" /></p>
</form>
</div>
</div>
</div>
""",
    },
}

for slug, p in PAGES.items():
    url = f"/{slug}/"
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "@id": url, "url": url, "name": p["title"].replace("&amp;", "&"),
             "isPartOf": {"@id": "/#website"}, "datePublished": "2019-04-02T21:14:09+00:00",
             "dateModified": "2026-03-14T18:05:37+00:00", "breadcrumb": {"@id": f"{url}#breadcrumb"},
             "inLanguage": "en-US"},
            {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
                {"@type": "ListItem", "position": 2, "name": p["crumb"]}]},
            {"@type": "WebSite", "@id": "/#website", "url": "/", "name": "Copperleaf Cycle Works",
             "description": "Bike repair in Marrow Falls", "publisher": {"@id": "/#organization"},
             "inLanguage": "en-US"},
            {"@type": "Organization", "@id": "/#organization", "name": "Copperleaf Cycle Works", "url": "/",
             "logo": {"@type": "ImageObject", "inLanguage": "en-US", "@id": "/#/schema/logo/image/",
                      "url": "/wp-content/uploads/2024/05/copperleaf-logo.png", "width": 512, "height": 512,
                      "caption": "Copperleaf Cycle Works"},
             "image": {"@id": "/#/schema/logo/image/"}},
        ],
    }
    head = home[:head_end]
    head = re.sub(r"<title>.*?</title>", f"<title>{p['title']}</title>", head)
    head = re.sub(r'(<meta (?:name|property)="(?:og:)?description" content=")[^"]*', lambda m: m.group(1) + p["desc"], head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + p["title"], head)
    head = head.replace('<meta property="og:type" content="website" />', '<meta property="og:type" content="article" />')
    head = head.replace('<link rel="canonical" href="/" />', f'<link rel="canonical" href="{url}" />')
    head = re.sub(r'(<script type="application/ld\+json" class="yoast-schema-graph">).*?(</script>)',
                  lambda m: m.group(1) + json.dumps(graph, separators=(",", ":")) + m.group(2), head, flags=re.S)
    body = home[head_end:body_start] + '<div class="entry-content clear" data-ast-blocks-layout="true" itemprop="text">\n' + p["content"] + "\n</div>\n" + home[body_end:]
    body = body.replace('class="home page-template-default page page-id-7', f'class="page-template-default page page-id-{p["id"]}')
    body = body.replace('id="post-7"', f'id="post-{p["id"]}"').replace('class="post-7 ', f'class="post-{p["id"]} ')
    body = body.replace(' current-menu-item page_item page-item-7 current_page_item', '').replace(' aria-current="page" class="menu-link"', ' class="menu-link"')
    out = ROOT / slug / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(head + body)
    print(out, len(head + body))
