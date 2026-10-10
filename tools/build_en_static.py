#!/usr/bin/env python3
"""英語の About / Privacy / Contact を作り、日本語の同名ページに英語版へのリンクと hreflang を足す（何度実行しても同じ結果）。"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://snowfield28.github.io/leak-ledger-data/"
FORM = sys.argv[1] if len(sys.argv) > 1 else "https://docs.google.com/forms/d/e/1FAIpQLScmk68QZJLTWugUYQF58kaNRV9CSfwQSGvBNsPpHZLyyH7VVQ/viewform"
UPD = "October 11, 2026"

ja_about = open(os.path.join(ROOT, "about.html"), encoding="utf-8").read()
CSS = re.search(r"<style>.*?</style>", ja_about, re.S).group(0)

def alt(name):
    return (f'<link rel="canonical" href="{SITE}en/{name}">\n<link rel="alternate" hreflang="ja" href="{SITE}{name}">\n'
            f'<link rel="alternate" hreflang="en" href="{SITE}en/{name}">\n<link rel="alternate" hreflang="x-default" href="{SITE}{name}">\n')

def page(name, title, desc, body):
    h = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} | Japan Data Breach Ledger</title>
<meta name="description" content="{desc}">
{alt(name)}{CSS}
</head>
<body><main>
<a class="back" href="./">← Back to the ledger</a>
<h1>{title}</h1>
<p class="upd">Last updated: {UPD}</p>
{body}
<nav class="foot" aria-label="Site information"><a href="./">Ledger</a><a href="case/">All incidents</a><a href="about.html">About</a><a href="privacy.html">Privacy policy</a><a href="contact.html">Contact / corrections</a><a href="../{name}" hreflang="ja" lang="ja">日本語</a></nav>
</main></body>
</html>
'''
    open(os.path.join(ROOT, "en", name), "w", encoding="utf-8").write(h)

page("about.html", "About this site",
 "Who runs the Japan Data Breach Ledger, what it lists, how incidents are verified, and its disclaimers.",
"""<section><h2>Operator</h2>
<p>snowfield28 (an individual)</p>
<p>This is an unofficial compilation run by an individual. It has no affiliation with the organizations or news outlets it mentions.</p></section>

<section><h2>What is listed</h2>
<p>Incidents of personal data leaks, or possible leaks, at companies, public bodies, universities, hospitals and organizations in Japan. Causes covered: cyber attacks, loss or theft, misdelivery or mis-posting, insider misconduct, and misconfiguration or bugs.</p></section>

<section><h2>Listing criteria</h2>
<ul>
<li>Incidents are found through news and security-news listings. <b>Only those whose own official announcement was opened and matched are listed.</b></li>
<li>Record counts, dates, data exposed, the organization's response and contact points follow what the official announcement says.</li>
<li>Incidents with no official announcement found, one that cannot be opened, or one that conflicts with other sources are not listed; they are kept as candidates and checked again.</li>
<li>Data is updated daily, and follow-ups (investigation results, corrected counts) are reflected when published.</li>
</ul></section>

<section><h2>Language</h2>
<p>Labels and categories are shown in English. The description of each incident (summary, investigation status, response) is shown in Japanese, as written in the official announcement; it is not machine-translated, so that no detail is altered. Please use the link to the official announcement for the original.</p></section>

<section><h2>How press and announcements are used</h2>
<ul>
<li>Summaries are written in this site's own words from facts in the official announcement and press coverage. Article text and headlines are not copied.</li>
<li>Press coverage is shown only as a lead and corroboration, by outlet name and link.</li>
<li>For details, follow the links to the original announcement or article.</li>
</ul></section>

<section><h2>Notes and disclaimer</h2>
<ul>
<li>Content reflects the official announcement at the time of checking and may change with later updates.</li>
<li>Counts are the organizations' own figures. They may mix people and records and may include duplicates.</li>
<li>"Possible leak" means the organization has not announced that a leak was confirmed.</li>
<li>A contact point's reception period may have ended. Check the official announcement for current information before contacting anyone.</li>
<li>Care is taken over accuracy, but errors may exist. The operator is not liable for damages arising from use of this information.</li>
</ul></section>

<section><h2>Corrections and other contact</h2>
<p>To report an error, a missing follow-up, or give feedback, use <a href="contact.html">Contact / corrections</a>. Reports are checked against the official announcement and corrected if needed.</p></section>
""")

page("privacy.html", "Privacy policy",
 "How the Japan Data Breach Ledger handles information.",
"""<section><h2>Information collected on this site</h2>
<p>This site itself does not ask visitors for names, email addresses or similar (the contact form is separate; see below). It uses no cookies and no analytics or advertising tools.</p>
<p>Settings on the site, such as filters, are processed only inside your device and are not sent to the operator.</p></section>

<section><h2>Records kept by the hosting provider</h2>
<p>This site is hosted on GitHub Pages (GitHub, Inc.). For security, GitHub logs and stores visitors' IP addresses. See <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">GitHub's Privacy Statement</a>. The operator does not receive these logs.</p></section>

<section><h2>Information you send through the contact form</h2>
<p>What you enter in the contact form (Google Forms) is used only to reply to you and to verify and correct the content of this site. It is not used for other purposes and is not provided to third parties except as required by law. Form responses are stored on Google LLC's services, and Google may use cookies on the form page. See <a href="https://policies.google.com/privacy" rel="noopener">Google's Privacy Policy</a>. Entering your name or email address is not required (give an email address only if you need a reply). Please do not enter passwords, credit card numbers or other information unrelated to your request.</p></section>

<section><h2>Links to other sites</h2>
<p>This site links to organizations' official announcements and news articles. How those sites handle information is governed by their own policies.</p></section>

<section><h2>Changes to this policy</h2>
<p>If handling changes, for example by adding analytics or advertising, this page will be updated before the change takes effect.</p></section>
""")

page("contact.html", "Contact / corrections",
 "Request a correction or contact the Japan Data Breach Ledger.",
f"""<section><h2>What we accept</h2>
<ul>
<li>Errors in listed content (record counts, dates, data exposed, contact points, etc.)</li>
<li>Missing follow-ups or final reports</li>
<li>Information about incidents not yet listed (please include the official announcement URL)</li>
<li>Feedback about the site</li>
</ul>
<p>For a correction request, including the URL of the official announcement that supports it lets us check faster. Reports are checked against the official announcement.</p>
<a class="btn" href="{FORM}" target="_blank" rel="noopener">Open the contact form (Japanese)</a>
<p class="muted">The form is written in Japanese; you may write your message in English.</p></section>

<section><h2>Please note</h2>
<p>This site is not a help desk for individual breaches. For questions about whether your own information was leaked, or about compensation, contact the organization's own contact point shown in each incident's details.</p>
<p>If you need a reply, enter your contact details in the form. Some messages may not receive a reply.</p></section>
""")

# JP pages: add hreflang alternates + English nav link (idempotent)
for name in ("about.html", "privacy.html", "contact.html"):
    p = os.path.join(ROOT, name)
    s = open(p, encoding="utf-8").read()
    if 'hreflang="en"' not in s:
        s = s.replace("<style>", f'<link rel="canonical" href="{SITE}{name}">\n<link rel="alternate" hreflang="ja" href="{SITE}{name}">\n<link rel="alternate" hreflang="en" href="{SITE}en/{name}">\n<link rel="alternate" hreflang="x-default" href="{SITE}{name}">\n<style>', 1)
        s = s.replace("</nav>", f'<a href="en/{name}" hreflang="en" lang="en">English</a></nav>', 1)
        open(p, "w", encoding="utf-8").write(s)
print("ok")
