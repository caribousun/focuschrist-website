#!/usr/bin/env python3
"""Permanent checks for the first-class Come, Follow Me study hub."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "come-follow-me.html").read_text(encoding="utf-8")
css = (ROOT / "come-follow-me.css").read_text(encoding="utf-8")
home = (ROOT / "index.html").read_text(encoding="utf-8")
home_css = (ROOT / "home.css").read_text(encoding="utf-8")
site_css = (ROOT / "site-system.css").read_text(encoding="utf-8")
about = (ROOT / "about.html").read_text(encoding="utf-8")
script = (ROOT / "come-follow-me.js").read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Come, Follow Me QA FAIL: {message}")


week_ids = re.findall(r",'(\d{2})'\]", script)
title_block = re.search(r"const titles=\[(.*?)\];", script, re.S)
titles = re.findall(r'"([^"]+)"', title_block.group(1)) if title_block else []

require(week_ids == [f"{number:02d}" for number in range(1, 53)], "weekly lesson IDs must cover 01 through 52")
require(len(titles) == 52, "every weekly lesson must have a title")
require(len(set(titles)) == 52, "weekly titles must be unique")
require(titles[0] == "The First Testament of Jesus Christ", "opening lesson title is not the official title")
require(titles[31] == "Thou Art Come … for Such a Time as This", "Esther lesson title is incomplete")
require("Jeremiah 31–33; 36–39; Lamentations 1; 3" in script, "October 26 lesson reading is incomplete")
require("data-cfm-current-title" in html, "current lesson title is not wired")
require(html.count("data-cfm-current-lesson") >= 2, "weekly lesson must be available in the main action and toolkit")
require("cfm-toolkit__grid" in html, "official study toolkit is missing")
require("003-improve-learning?lang=eng" in html, "official learning guidance is missing")
require("004-old-testament-overview?lang=eng" in html, "official Old Testament overview is missing")
require("document.querySelectorAll('[data-cfm-current-lesson]')" in script, "all current-lesson links must update together")
require("new Date(w[1]+'T12:00:00')" in script, "cross-month lessons must be grouped by their ending month")
require("align-items:start" in css, "schedule cards may stretch into empty panels")
require(".cfm-btn--gold" in css and "color:var(--cfm-navy)!important" in css, "primary button contrast is not locked")
require(".cfm-btn:not(.cfm-btn--gold):hover" in css, "generic hover styling may override the gold action")
require('href="pioneers.html">PIONEERS</a>' in html, "desktop and mobile study navigation must include Pioneers")
require("fc-cfm-home__highlights" in home, "Home study preview is not enriched")
require('href="come-follow-me.html#year-schedule"' in home, "Home schedule route is missing")
require('margin-top: 22px' in home_css, "Home action row does not match the standard desktop clearance")
require('margin-top: 18px' in home_css, "Home action row does not match the standard mobile clearance")
require(".fc-actions--content { margin-top: 22px; }" in site_css, "shared content actions need 22px desktop clearance")
require(".fc-actions--content { margin-top: 18px; }" in site_css, "shared content actions need 18px mobile clearance")
require("fc-actions--content" in about, "About closing actions must use the shared responsive clearance")
require("fc-actions--center fc-actions--content" in home, "Home closing actions must use the shared responsive clearance")
require('style="margin-top:22px;"' not in about, "inline About spacing blocks the mobile standard")

print("focusChrist COME, FOLLOW ME HUB QA PASSED")
print("Verified 52 weekly routes and titles, official study toolkit, dynamic lesson links, schedule containment, action contrast, and Home spacing controls.")
