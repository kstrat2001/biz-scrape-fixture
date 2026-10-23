"""Builds the Wix variant: the same shop and the same facts as the WordPress
variant, in the markup a Wix (Thunderbolt) site serves to curl.

Wix renders pages server-side, so the text is in the HTML, but buried in
generated ids and classes, with very large inline JSON and script blocks. Those
blocks are cut to a representative size here so a page fits a small model's
context; the README says so. Links are root-relative (a real Wix site uses
absolute links on its own domain) so the pages work from a local server.

Run once when the content changes; the generated files are committed.
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "site" / "wix"
MEDIA = "https://static.wixstatic.com/media/3f1c2a_8d2e41b0c9a74f5e9b1d6c0a7e2f4b19~mv2.png"


def cid(seed):
    """A stable Wix-style component id, e.g. comp-lq3x9a2b."""
    return "comp-l" + hashlib.sha1(seed.encode()).hexdigest()[:7]


def rich(seed, *paras, font="font_8"):
    ps = "".join(
        f'<p class="{font} wixui-rich-text__text" style="font-size:16px;"><span style="font-size:16px;" class="wixui-rich-text__text">{p}</span></p>'
        for p in paras
    )
    c = cid(seed)
    return f'<div id="{c}" class="HcOXKn SxM0TO QxJLC3 {c} wixui-rich-text" data-testid="richTextElement">{ps}</div>\n'


def heading(seed, text, tag="h2", font="font_2"):
    c = cid(seed)
    return f'<div id="{c}" class="HcOXKn SxM0TO QxJLC3 {c} wixui-rich-text" data-testid="richTextElement"><{tag} class="{font} wixui-rich-text__text">{text}</{tag}></div>\n'


def button(seed, label, href):
    c = cid(seed)
    return (f'<div class="{c} wixui-button" id="{c}" aria-disabled="false"><a data-testid="linkElement" href="{href}" target="_self" class="uDW_Qe wixui-button PlZyDq" aria-disabled="false">'
            f'<span class="l7_2fn wixui-button__label">{label}</span></a></div>\n')


def section(seed, inner):
    c = cid(seed)
    return (f'<section id="{c}" tabIndex="-1" class="Oqnisf {c} wixui-section" data-block-level-container="Section">'
            f'<div id="bgLayers_{c}" data-hook="bgLayers" data-motion-part="BG_LAYER {c}" class="MW5IWV"><div data-testid="colorUnderlay" class="LWbAav Kv1aVt"></div><div id="bgMedia_{c}" data-motion-part="BG_MEDIA {c}" class="VgO9Yg"></div></div>'
            f'<div data-testid="columns" class="V5AUxf"><div id="{c}-col" class="comp-col wixui-column-strip__column"><div data-mesh-id="{c}inlineContent" data-testid="inline-content" class=""><div data-mesh-id="{c}inlineContent-gridContainer" data-testid="mesh-container-content">\n'
            + inner + "</div></div></div></div></section>\n")


NAV = [("Home", "/"), ("Services", "/book-online"), ("About", "/about-us"), ("Contact", "/contact")]

LOCAL_BUSINESS = {
    "@context": "https://schema.org/",
    "@type": "LocalBusiness",
    "name": "Copperleaf Cycle Works",
    "url": "/",
    "image": MEDIA,
    "telephone": "541-555-0142",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "418 Tannery Row, Unit B",
        "addressLocality": "Marrow Falls",
        "addressRegion": "OR",
        "postalCode": "97999",
        "addressCountry": "US",
    },
}


def head(title, desc, path, page_id):
    viewer = {
        "site": {"metaSiteId": "6b0f3c2e-91d4-4a77-b2c8-0e5d1f7a9c33", "siteId": "a41d2c9e-7b3f-4e18-9c55-d2e8f0b6a174",
                 "externalBaseUrl": "", "isWixSite": False, "isPremium": True, "language": "en", "locale": "en-us",
                 "currency": "USD", "timeZone": "America/Los_Angeles", "regionalLanguage": "en"},
        "requestUrl": path, "fleetConfig": {"fleetName": "thunderbolt-renderer-user-code", "type": "GA", "code": 0},
        "mode": {"qa": False, "enableTestApi": False, "debug": False, "ssrIndicator": False, "ssrOnly": False,
                 "siteAssetsFallback": "enable", "versionIndicator": False},
        "siteFeatures": ["accessibility", "animations", "assetsLoader", "businessLogger", "captcha", "clickHandlerRegistrar",
                         "commonConfig", "componentsLoader", "consentPolicy", "cyclicTabbing", "dynamicPages", "environment",
                         "lightbox", "navigation", "ooi", "pageScroll", "renderer", "router", "scrollRestoration", "seo",
                         "siteMembers", "siteScrollBlocker", "tpa", "translations", "usedPlatformApis", "warmupData", "windowScroll"],
        "siteFeaturesConfigs": {"seo": {"context": {"siteName": "Copperleaf Cycle Works", "siteUrl": "", "indexSite": True,
                                                    "defaultUrl": "", "currLangCode": "en"}, "metaTags": [{"name": "generator", "content": "Wix.com Website Builder"}]}},
        "pageId": page_id, "experiments": {"specs.thunderbolt.ssrImageOptimization": True, "specs.thunderbolt.fetchPriority": True,
                                           "specs.thunderbolt.useClassSelectorsForCss": True, "specs.thunderbolt.deferredHydration": True},
    }
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset='utf-8'>
  <meta name="viewport" content="width=device-width, initial-scale=1" id="wixDesktopViewport" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="generator" content="Wix.com Website Builder"/>
  <link rel="icon" sizes="192x192" href="{MEDIA}/v1/fill/w_192%2Ch_192%2Clg_1%2Cusm_0.66_1.00_0.01/3f1c2a_8d2e41b0c9a74f5e9b1d6c0a7e2f4b19~mv2.png" type="image/png"/>
  <link rel="shortcut icon" href="{MEDIA}/v1/fill/w_32%2Ch_32%2Clg_1%2Cusm_0.66_1.00_0.01/3f1c2a_8d2e41b0c9a74f5e9b1d6c0a7e2f4b19~mv2.png" type="image/png"/>
  <script type="text/javascript">
    window.__BROWSER_DEPRECATION__ = !('noModule' in HTMLScriptElement.prototype) || !('fetch' in window) || !('IntersectionObserver' in window);
  </script>
  <script id="wix-viewer-model" type="application/json">{json.dumps(viewer, separators=(",", ":"))}</script>
  <script type="application/json" id="wix-essential-viewer-model">{{"fleetConfig":{{"fleetName":"thunderbolt-renderer-user-code","type":"GA","code":0}},"mode":{{"qa":false,"enableTestApi":false,"debug":false}},"componentsLibrariesTopology":[{{"artifactId":"editor-elements","namespace":"wixui","url":"https://static.parastorage.com/services/editor-elements/1.13240.0"}}],"siteFeaturesConfigs":{{"sessionManager":{{"isRunningInDifferentSiteContext":false}}}},"siteAssets":{{"clientTopology":{{"mediaRootUrl":"https://static.wixstatic.com","staticMediaUrl":"https://static.wixstatic.com/media","moduleRepoUrl":"https://static.parastorage.com/unpkg","fileRepoUrl":"https://static.parastorage.com/services","siteAssetsUrl":"https://siteassets.parastorage.com","pageJsonServerUrls":["https://pages.parastorage.com","https://staticorigin.wixstatic.com","https://fallback.wix.com/wix-html-editor-pages-webapp/page"],"pathOfTBModulesInFileRepoForFallback":"wix-thunderbolt/dist/"}}}}}}</script>
  <script src="https://static.parastorage.com/services/wix-thunderbolt/dist/main.4a7d1c8e.bundle.min.js" async></script>
  <script src="https://static.parastorage.com/unpkg/react@18.3.1/umd/react.production.min.js" defer></script>
  <script src="https://static.parastorage.com/unpkg/react-dom@18.3.1/umd/react-dom.production.min.js" defer></script>
  <!-- warmup data and the remaining Thunderbolt bundles (several hundred KB on a live Wix page) are cut from this fixture -->
  <title>{title}</title>
  <meta name="description" content="{desc}"/>
  <link rel="canonical" href="{path}"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{desc}"/>
  <meta property="og:image" content="{MEDIA}/v1/fill/w_1200%2Ch_630%2Cal_c/3f1c2a_8d2e41b0c9a74f5e9b1d6c0a7e2f4b19~mv2.png"/>
  <meta property="og:url" content="{path}"/>
  <meta property="og:site_name" content="Copperleaf Cycle Works"/>
  <meta property="og:type" content="website"/>
  <script type="application/ld+json">{json.dumps(LOCAL_BUSINESS, separators=(",", ":"))}</script>
  <meta name="twitter:card" content="summary_large_image"/>
  <style id="css_masterPage">
#SITE_CONTAINER{{--bg:var(--color_11);--rd:0px;--shd:none;}}#masterPage{{--pinned-layer-in-container-{cid('mp')}:51;--above-all-in-container:49}}.HcOXKn{{direction:var(--text-direction);min-height:var(--min-height);min-width:var(--min-width)}}.HcOXKn .SxM0TO{{word-wrap:break-word;height:100%;overflow-wrap:break-word;position:relative;width:100%}}.uDW_Qe{{align-items:center;box-sizing:border-box;display:flex;justify-content:var(--label-align);min-width:100%;text-align:initial;width:-moz-max-content;width:max-content}}.font_2{{font:normal normal normal 40px/1.2em playfair display,serif;color:#2f2e2e}}.font_8{{font:normal normal normal 16px/1.6em avenir-lt-w01_35-light1475496,sans-serif;color:#605e5e}}
  </style>
</head>
"""


def page(title, desc, path, page_id, sections):
    nav = "".join(
        f'<li class="wixui-horizontal-menu__item" data-testid="menuItemDepth0"><a data-testid="linkElement" href="{href}" target="_self" class="UiHgGh"'
        + (' aria-current="page"' if href == path else "")
        + f'><div class="itemDepth02233374943__itemWrapper"><span class="itemDepth02233374943__label wixui-horizontal-menu__item-label">{label}</span></div></a></li>'
        for label, href in NAV
    )
    header = (
        '<header id="SITE_HEADER" class="xU8fqS SITE_HEADER wixui-header" tabIndex="-1"><div class="_C0cVf"><div class="_4XcTfy" data-testid="screenWidthContainerBgCenter"></div></div><div class="U4Bvut"><div class="G5K6X8"></div><div class="gUbusX" data-testid="headerInlineContent"><div data-mesh-id="SITE_HEADERinlineContent-gridContainer" data-testid="mesh-container-content">\n'
        + f'<div id="{cid("logo")}" class="MazNVa {cid("logo")} wixui-image"><a data-testid="linkElement" href="/" target="_self" class="j7pOnl"><wow-image id="img_{cid("logo")}" class="HlRz5e BI8PVQ" data-image-info="{{&quot;containerId&quot;:&quot;{cid("logo")}&quot;,&quot;displayMode&quot;:&quot;fill&quot;}}" data-bg-effect-name="" data-has-ssr-src=""><img src="{MEDIA}/v1/fill/w_160,h_48,al_c,q_85,enc_avif,quality_auto/copperleaf-logo.png" alt="Copperleaf Cycle Works logo" style="width:160px;height:48px;object-fit:cover" width="160" height="48"/></wow-image></a></div>\n'
        + f'<wix-dropdown-menu id="{cid("nav")}" class="XRwtpn NHM1d1 {cid("nav")} wixui-dropdown-menu hidden-during-prewarmup" tabIndex="-1" dir="ltr" data-stretch-buttons-to-menu-width="true" data-same-width-buttons="false" data-num-items="4" data-menuborder-y="0" data-menubtn-border="0" data-ribbon-els="0" data-label-pad="0" data-ribbon-extra="0" data-dropalign="center"><nav class="R_TAzU" id="{cid("nav")}navContainer" aria-label="Site"><ul class="y7qwii" id="{cid("nav")}itemsContainer" style="text-align:center">{nav}</ul></nav></wix-dropdown-menu>\n'
        + f'<div id="{cid("hdrphone")}" class="HcOXKn SxM0TO QxJLC3 {cid("hdrphone")} wixui-rich-text" data-testid="richTextElement"><p class="font_8 wixui-rich-text__text"><a href="tel:5415550142" class="wixui-rich-text__text">541-555-0142</a></p></div>\n'
        + "</div></div></div></header>\n"
    )
    footer = (
        '<footer id="SITE_FOOTER" class="xU8fqS SITE_FOOTER wixui-footer" tabIndex="-1"><div class="_C0cVf"><div class="_4XcTfy" data-testid="screenWidthContainerBgCenter"></div></div><div class="U4Bvut"><div class="G5K6X8"></div><div class="gUbusX" data-testid="footerInlineContent"><div data-mesh-id="SITE_FOOTERinlineContent-gridContainer" data-testid="mesh-container-content">\n'
        + rich("f-addr", "418 Tannery Row, Unit B", "Marrow Falls, OR 97999")
        + rich("f-contact", '<a href="tel:5415550142" class="wixui-rich-text__text">541-555-0142</a>', '<a href="mailto:hello@copperleaf-cycles.example" class="wixui-rich-text__text">hello@copperleaf-cycles.example</a>')
        + rich("f-parts", "Parts orders only: 541-555-0177")
        + rich("f-copy", "&copy; 2026 by Copperleaf Cycle Works. Proudly created with Wix.com")
        + "</div></div></div></footer>\n"
    )
    body = (
        '<body class="">\n<div id="SITE_CONTAINER"><div id="main_MF" class="main_MF"><div id="SCROLL_TO_TOP" class="Vd6aQZ ignore-focus SCROLL_TO_TOP" role="region" tabIndex="-1" aria-label="top of page"><span class="mHZSwn">top of page</span></div>'
        '<div id="site-root" class="site-root"><div id="masterPage" class="mesh-layout masterPage css-editing-scope">\n'
        '<div id="soapAfterHeader"><a class="skip-to-content" href="#PAGES_CONTAINER">Skip to Main Content</a></div>\n'
        + header
        + f'<main id="PAGES_CONTAINER" tabIndex="-1" data-main-content="true"><div id="SITE_PAGES" class="JsJXaX SITE_PAGES"><div id="{page_id}" class="dBAkHi theme-vars"><div class="PFkO7r wixui-page" data-testid="page-bg"></div><div class="HT5ybB"><div id="Containers{page_id}" class="Containers{page_id} SPY_vo"><div id="{page_id}inlineContent" class="nTOEE9">\n'
        + "".join(section(f"{page_id}-{i}", s) for i, s in enumerate(sections))
        + "</div></div></div></div></div></main>\n"
        + footer
        + '</div></div></div></div>\n<div id="SCROLL_TO_BOTTOM" class="Vd6aQZ ignore-focus SCROLL_TO_BOTTOM" role="region" tabIndex="-1" aria-label="bottom of page"><span class="mHZSwn">bottom of page</span></div>\n'
        '<script type="text/javascript">window.thunderboltVersion = "1.15212.0"; window.clientSideRender = false;</script>\n'
        "</body>\n</html>\n"
    )
    return head(title, desc, path, page_id) + body


PAGES = {
    "": page(
        "Bike Repair | Copperleaf Cycle Works | Marrow Falls",
        "Friendly, independent bike repair in Marrow Falls. Tune-ups, flat repairs, wheel truing, brakes and e-bike service. Walk-ins welcome Tuesday to Saturday.",
        "/", "c1dmp",
        [
            heading("h1", "Keep your bike rolling.", tag="h1")
            + rich("hero", "Independent, family-owned bike repair in Marrow Falls since 2011.")
            + button("cta", "Book a Tune-Up", "/book-online"),
            heading("fix", "What We Fix")
            + rich("fix1", "<strong>Tune-Ups</strong>", "Gears, brakes and bearings adjusted so your ride feels new again.")
            + rich("fix2", "<strong>Flat Tire Repair</strong>", "Most flats fixed while you wait.")
            + rich("fix3", "<strong>E-Bike Service</strong>", "Hub and mid-drive e-bikes, batteries checked on every visit.")
            + button("all", "See Everything We Do", "/book-online"),
            heading("trust", "Why Riders Trust Us")
            + rich("trust1", "Every mechanic is certified by the Pacific Bicycle Mechanics Guild", "30-day guarantee on all repair work", "Over 400 five-star reviews from riders across the Linden Valley")
            + rich("quote", "&ldquo;They trued my wheel in twenty minutes and wouldn&rsquo;t take a tip. Best shop in the valley.&rdquo;", "&mdash; Dana R., Marrow Falls", font="font_9"),
            heading("visit", "Visit the Shop")
            + rich("visit1", "We&rsquo;re on Tannery Row, two doors down from the old feed mill. Free parking out back. We serve riders in Marrow Falls and across the Linden Valley.")
            + heading("hrs", "Opening Hours", tag="h3", font="font_5")
            + rich("hrs1", "Tue &ndash; Fri: 9:30 AM &ndash; 6:00 PM", "Sat: 9:00 AM &ndash; 4:00 PM", "Sun &ndash; Mon: Closed"),
        ],
    ),
    "book-online": page(
        "Services &amp; Prices | Copperleaf Cycle Works",
        "Bike repair services and prices at Copperleaf Cycle Works in Marrow Falls.",
        "/book-online", "x7k2p",
        [
            heading("bo-h", "Services", tag="h1")
            + rich("bo-intro", "Every job starts with a free safety check. Prices include labor; parts are extra unless noted."),
            "".join(
                f'<div data-hook="service-card" class="sHx2pQ {cid("svc"+n)}"><div data-hook="info-container" class="tFrX0B">'
                f'<h2 data-hook="service-info-title-text" class="sVu7cnw">{n}</h2>'
                f'<p data-hook="service-info-details-text" class="sk2gxa1">{d}</p>'
                f'<p data-hook="service-info-price" class="sX1aB9z"><span aria-hidden="true">{p}</span><span class="sr-only">{sr}</span></p>'
                f'</div><button data-hook="book-button" class="sCcNcuG oi9Z4Mn" aria-label="Book Now: {n}">Book Now</button></div>\n'
                for n, d, p, sr in [
                    ("Basic Tune-Up", "1 hr", "$79", "79 US dollars"),
                    ("Full Overhaul", "4 hr", "from $189", "from 189 US dollars"),
                    ("Flat Tire Repair", "30 min &middot; tube included", "$15", "15 US dollars"),
                    ("Wheel Truing", "30 min &middot; per wheel", "$25", "25 US dollars"),
                    ("Brake Service", "45 min &middot; per wheel", "$35", "35 US dollars"),
                    ("Bike Fitting", "1 hr 30 min", "$120", "120 US dollars"),
                    ("E-Bike Service", "Varies", "Call for a quote", "Call for a quote"),
                ]
            )
            + rich("bo-note", "Most tune-ups are ready within two business days. Need it sooner? Ask about same-day service."),
        ],
    ),
    "about-us": page(
        "About | Copperleaf Cycle Works",
        "Copperleaf Cycle Works has kept Marrow Falls riding since 2011.",
        "/about-us", "q4n8r",
        [
            heading("ab-h", "About Us", tag="h1")
            + rich("ab1", "Copperleaf Cycle Works opened in 2011 in a one-bay garage on Tannery Row. Fifteen years later we&rsquo;re still a family shop, just with a bigger bay and more stands.")
            + rich("ab2", "Our mechanics are certified by the Pacific Bicycle Mechanics Guild, and every repair carries our 30-day guarantee. We work on road, mountain, kids&rsquo; and cargo bikes, and on most e-bikes.")
            + rich("ab3", "We&rsquo;re proud members of the Linden Valley Chamber of Commerce."),
        ],
    ),
    "contact": page(
        "Contact | Copperleaf Cycle Works",
        "Find Copperleaf Cycle Works on Tannery Row in Marrow Falls. Call, email or send us a message.",
        "/contact", "m9t3w",
        [
            heading("ct-h", "Contact", tag="h1")
            + heading("ct-v", "Visit", tag="h3", font="font_5")
            + rich("ct-addr", "418 Tannery Row, Unit B", "Marrow Falls, OR 97999")
            + heading("ct-c", "Call or Email", tag="h3", font="font_5")
            + rich("ct-tel", 'Phone: <a href="tel:5415550142" class="wixui-rich-text__text">541-555-0142</a>', 'Email: <a href="mailto:hello@copperleaf-cycles.example" class="wixui-rich-text__text">hello@copperleaf-cycles.example</a>')
            + heading("ct-hr", "Hours", tag="h3", font="font_5")
            + rich("ct-hrs", "Monday: Closed", "Tuesday &ndash; Friday: 9:30 AM &ndash; 6:00 PM", "Saturday: 9:00 AM &ndash; 4:00 PM", "Sunday: Closed")
            + rich("ct-hol", "<em>Holiday hours: closed Thanksgiving Day and December 25.</em>"),
            heading("ct-f", "Book a Repair")
            + f'<form id="{cid("form")}" class="wixui-form" data-testid="form" aria-label="Contact form"><div class="wixui-text-input"><label for="input_{cid("n")}">Name</label><input id="input_{cid("n")}" type="text" name="first-name" required="" aria-required="true"/></div>'
            f'<div class="wixui-text-input"><label for="input_{cid("e")}">Email</label><input id="input_{cid("e")}" type="email" name="email" required="" aria-required="true"/></div>'
            f'<div class="wixui-text-box"><label for="textarea_{cid("m")}">What does your bike need?</label><textarea id="textarea_{cid("m")}" name="message"></textarea></div>'
            f'<button type="submit" class="wixui-button">Submit</button></form>\n',
        ],
    ),
}

for slug, html in PAGES.items():
    out = ROOT / slug / "index.html" if slug else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(out, len(html))
