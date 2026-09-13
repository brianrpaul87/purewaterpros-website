from pathlib import Path
import re
import subprocess
import sys

root = Path(sys.argv[1]).resolve()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


image = root / "assets/ro-install/ro-install-langford-q78.webp"
if not image.is_file() or image.stat().st_size != 45012:
    raise SystemExit(f"RO image missing or wrong size: {image}")

# Homepage
index_path = root / "index.html"
index = index_path.read_text(encoding="utf-8")
index = replace_once(
    index,
    ".field-experience-card:first-child img{object-fit:contain;padding:8px;background:#f8fbfc}",
    ".field-experience-card:first-child img{object-fit:cover;padding:0;background:#eaf3f6}",
    "homepage first-card image styling",
)

section_start = index.index('<section class="field-experience-section"')
section_end = index.index('<section class="about-section"', section_start)
block = index[section_start:section_end]

old_intro = '<div class="field-experience-intro"><p class="eyebrow">Field experience</p><h2 id="field-experience-title">A few examples from prior hands-on work.</h2><p>These are examples from Brian Paul’s earlier water-treatment field work, before Pure Water Pros launched in British Columbia.</p></div>'
new_intro = '<div class="field-experience-intro"><p class="eyebrow">Installation &amp; field experience</p><h2 id="field-experience-title">Real water-treatment work, not catalogue photos.</h2><p>A mix of Pure Water Pros installation work in British Columbia and examples from Brian Paul’s earlier hands-on water-treatment experience.</p></div>'
block = replace_once(block, old_intro, new_intro, "homepage field-experience intro")

if "6%20Stage%20Traditional%20RO%20System" not in block:
    raise SystemExit("homepage first RO card: historical RO image not found")

new_figure = '<figure class="field-experience-card"><picture><img src="/assets/ro-install/ro-install-langford-q78.webp" alt="Pure Water Pros under-sink reverse osmosis installation with storage tank and leak-detection tray" loading="lazy" decoding="async" width="1200" height="900"/></picture><figcaption><strong>Complete under-sink reverse osmosis</strong><span>Pure Water Pros RO installation with storage tank. New installations include faucet installation and a leak-detection tray beneath the system.</span></figcaption></figure>'
block, figure_count = re.subn(
    r'<figure class="field-experience-card">.*?</figure>',
    new_figure,
    block,
    count=1,
    flags=re.S,
)
if figure_count != 1:
    raise SystemExit(f"homepage first RO card: expected 1 figure replacement, got {figure_count}")

block = replace_once(
    block,
    "Shown as prior field experience, not as current Pure Water Pros project photos. Equipment brands shown do not imply dealer affiliation.",
    "Photos shown include Pure Water Pros work in British Columbia and prior field experience. Equipment brands shown do not imply dealer affiliation.",
    "homepage field-experience note",
)
index = index[:section_start] + block + index[section_end:]
index_path.write_text(index, encoding="utf-8")

# RO service page
ro_path = root / "reverse-osmosis-victoria.html"
ro = ro_path.read_text(encoding="utf-8")
ro = replace_once(
    ro,
    '<article class="card"><h3>New RO systems</h3><p>Under-sink systems selected around water quality, available pressure, space and household expectations.</p></article>',
    '<article class="card"><h3>New RO systems</h3><p>Under-sink systems selected around water quality, available pressure and space, with faucet installation and a leak-detection tray included with every new installation.</p></article>',
    "RO new-systems card",
)

how_anchor = '<section class="content-section alt">\n<div class="shell two-col">\n<div>\n<p class="eyebrow">How it works</p>'
if ro.count(how_anchor) != 1:
    raise SystemExit(f"RO how-it-works anchor: expected 1 match, found {ro.count(how_anchor)}")

value_section = '''<section class="content-section alt">
<div class="shell two-col">
<figure class="service-example"><img alt="Pure Water Pros under-sink reverse osmosis installation with storage tank and leak-detection tray" decoding="async" height="900" loading="lazy" src="/assets/ro-install/ro-install-langford-q78.webp" width="1200"/><figcaption>Recent Pure Water Pros under-sink RO installation</figcaption></figure>
<div class="prose">
<p class="eyebrow">Complete RO installation</p>
<h2>The details are part of the install.</h2>
<p>Every new Pure Water Pros under-sink RO installation includes a leak-detection tray beneath the system at no additional charge.</p>
<p>We also handle the dedicated drinking-water faucet installation, including drilling the sink or countertop where appropriate. If a specialty surface or unusual site condition needs different handling, we identify that before the work begins.</p>
<aside class="info-panel">
<p class="eyebrow">Clear installed pricing</p>
<h2>Compare the complete installed job.</h2>
<p>Standard faucet installation and the included leak-detection tray are part of the installed quote, so the basic installation scope is clear up front. Specialty stone, porcelain or unusual site work is identified before installation.</p>
</aside>
</div>
</div>
</section>
<section class="content-section">
<div class="shell two-col">
<div>
<p class="eyebrow">How it works</p>'''
ro = ro.replace(how_anchor, value_section, 1)

if ro.count("/assets/ro-install/ro-install-langford-q78.webp") != 1:
    raise SystemExit("RO service page should reference the new install image exactly once")
if "beat the competition" in ro.lower() or "price match" in ro.lower():
    raise SystemExit("blanket competition pricing promise unexpectedly present")
ro_path.write_text(ro, encoding="utf-8")

# Mechanical scope check
subprocess.run(["git", "-C", str(root), "diff", "--check"], check=True)
changed = subprocess.check_output(
    ["git", "-C", str(root), "diff", "--name-only"], text=True
).splitlines()
expected = ["index.html", "reverse-osmosis-victoria.html"]
if sorted(changed) != sorted(expected):
    raise SystemExit(f"unexpected source changed-file set: {changed}")

print("Source staging verified: index.html + reverse-osmosis-victoria.html only")
