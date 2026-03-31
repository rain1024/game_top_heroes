import requests
from bs4 import BeautifulSoup
import os
import re
import time

BASE_URL = "https://topheroes1.fandom.com"

PAGES = [
    "Heroes",
    "Adjudicator", "Astrologer", "Bard", "Bishop", "Hostess", "Knight",
    "Minister", "Nun", "Paragon", "Pyromancer", "Ranger", "Rose_Princess",
    "Secret_Keeper", "Warrior", "Wizard",
    "Dancer", "Druid", "Priestess", "Forest_Maiden", "Pathfinder", "Pixie",
    "Sage", "Stonemanson", "Treeguard", "Watcher", "Windwalker",
    "Monk", "Tidecaller", "Archer", "Pharmacist",
    "Barbarian", "Outlaw", "Shaman", "Storm_Maiden", "Warlock",
    "Wilderness_Hunter", "Desert_Prince", "Witch", "Swordmaster",
    "Soulmancer", "Headhunter", "Rogue", "Blacksmith", "Guard",
    "World_Creatures", "World_Boss", "Slime_King", "Leopard", "Death_Knight",
    "Ruby_Mine_Guard", "Timber_Guard", "Stone_Guard",
    "Dark_Legionaires", "Root_Ghouls", "Rally_Boss", "Legion_Boss",
    "Black_Dragons", "Red_Dragons", "Trolls", "Yetis", "Boars",
    "Soldiers",
    "Heroes_Leveling_Items", "Recruitment_Tickets", "Heroes_Gear_Shards",
    "Heroes_Shards", "Faction_Boxes", "Soul_Stones",
    "Buildings", "PvP_Buildings", "PvE_Buildings", "World_Map_Buildings",
    "PvE_Techs", "PvP_Techs",
    "Lord_Gears_%26_Runes", "Lord_Gears", "Runes",
    "Gears", "Crafting_Materials", "Relics", "Legendaries", "Epic", "Rare",
    "Kingdom_Vs_Kingdom", "Guild_Arm_Race", "Ancient_Battlefield",
    "Dark_Invasion", "Guild_Boss", "Guild_Carriage",
    "Arena", "Carriages", "Daily_Bounties",
    "Frequently_Asked_Questions", "Local_Sitemap",
]

KNOWLEDGEBASE_DIR = "knowledgebase"


def slugify(name):
    return name.replace("%26", "and").replace(" ", "_")


def get_category(page_name):
    hero_names = {
        "Adjudicator", "Astrologer", "Bard", "Bishop", "Hostess", "Knight",
        "Minister", "Nun", "Paragon", "Pyromancer", "Ranger", "Rose_Princess",
        "Secret_Keeper", "Warrior", "Wizard", "Dancer", "Druid", "Priestess",
        "Forest_Maiden", "Pathfinder", "Pixie", "Sage", "Stonemanson",
        "Treeguard", "Watcher", "Windwalker", "Monk", "Tidecaller", "Archer",
        "Pharmacist", "Barbarian", "Outlaw", "Shaman", "Storm_Maiden",
        "Warlock", "Wilderness_Hunter", "Desert_Prince", "Witch",
        "Swordmaster", "Soulmancer", "Headhunter", "Rogue", "Blacksmith",
        "Guard", "Heroes",
    }
    creature_names = {
        "World_Creatures", "World_Boss", "Slime_King", "Leopard",
        "Death_Knight", "Ruby_Mine_Guard", "Timber_Guard", "Stone_Guard",
        "Dark_Legionaires", "Root_Ghouls", "Rally_Boss", "Legion_Boss",
        "Black_Dragons", "Red_Dragons", "Trolls", "Yetis", "Boars", "Soldiers",
    }
    item_names = {
        "Heroes_Leveling_Items", "Recruitment_Tickets", "Heroes_Gear_Shards",
        "Heroes_Shards", "Faction_Boxes", "Soul_Stones",
    }
    building_names = {
        "Buildings", "PvP_Buildings", "PvE_Buildings", "World_Map_Buildings",
    }
    tech_names = {"PvE_Techs", "PvP_Techs"}
    gear_names = {
        "Lord_Gears_%26_Runes", "Lord_Gears", "Runes", "Gears",
        "Crafting_Materials", "Relics", "Legendaries", "Epic", "Rare",
    }
    event_names = {
        "Kingdom_Vs_Kingdom", "Guild_Arm_Race", "Ancient_Battlefield",
        "Dark_Invasion", "Guild_Boss", "Guild_Carriage", "Arena",
        "Carriages", "Daily_Bounties",
    }

    if page_name in hero_names:
        return "heroes"
    elif page_name in creature_names:
        return "creatures"
    elif page_name in item_names:
        return "items"
    elif page_name in building_names:
        return "buildings"
    elif page_name in tech_names:
        return "techs"
    elif page_name in gear_names:
        return "gears"
    elif page_name in event_names:
        return "events"
    else:
        return "general"


def parse_wiki_page(html, page_name):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one(".mw-parser-output")
    if not content:
        return None

    # Remove navigation/TOC elements
    for el in content.select(".toc, .mw-editsection, script, style, .navbox"):
        el.decompose()

    lines = []

    for el in content.children:
        if not hasattr(el, "name") or el.name is None:
            text = el.string
            if text and text.strip():
                lines.append(text.strip())
            continue

        if el.name in ("h1", "h2"):
            heading = el.get_text(strip=True)
            lines.append(f"\n## {heading}\n")
        elif el.name == "h3":
            heading = el.get_text(strip=True)
            lines.append(f"\n### {heading}\n")
        elif el.name == "h4":
            heading = el.get_text(strip=True)
            lines.append(f"\n#### {heading}\n")
        elif el.name == "p":
            text = el.get_text(strip=True)
            if text:
                lines.append(text)
        elif el.name == "ul":
            for li in el.find_all("li", recursive=False):
                lines.append(f"- {li.get_text(strip=True)}")
        elif el.name == "ol":
            for i, li in enumerate(el.find_all("li", recursive=False), 1):
                lines.append(f"{i}. {li.get_text(strip=True)}")
        elif el.name == "table":
            rows = el.find_all("tr")
            if not rows:
                continue
            table_lines = []
            for row in rows:
                cells = row.find_all(["th", "td"])
                cell_texts = [c.get_text(strip=True).replace("|", "/") for c in cells]
                if cell_texts:
                    table_lines.append("| " + " | ".join(cell_texts) + " |")
            if len(table_lines) > 0:
                # Add separator after first row (header)
                ncols = table_lines[0].count("|") - 1
                sep = "| " + " | ".join(["---"] * ncols) + " |"
                table_lines.insert(1, sep)
                lines.append("")
                lines.extend(table_lines)
                lines.append("")
        elif el.name == "div":
            text = el.get_text(strip=True)
            if text and len(text) > 10:
                lines.append(text)

    return "\n".join(lines)


def fetch_via_api(page_name):
    """Use MediaWiki API to get parsed HTML content."""
    api_url = f"{BASE_URL}/api.php"
    params = {
        "action": "parse",
        "page": page_name,
        "prop": "text",
        "format": "json",
        "disabletoc": "true",
    }
    headers = {
        "User-Agent": "TopHeroesWikiCrawler/1.0 (game knowledge base project)",
    }
    try:
        resp = requests.get(api_url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            print(f"  API ERROR {page_name}: {data['error'].get('info', 'unknown')}")
            return None
        html = data["parse"]["text"]["*"]
        return html
    except Exception as e:
        print(f"  ERROR fetching {page_name}: {e}")
        return None


def crawl_page(page_name):
    html = fetch_via_api(page_name)
    if not html:
        return None

    content_md = parse_wiki_page(html, page_name)
    if not content_md:
        print(f"  SKIP {page_name}: no content")
        return None

    url = f"{BASE_URL}/wiki/{page_name}"
    title = page_name.replace("_", " ").replace("%26", "&")
    category = get_category(page_name)
    slug = slugify(page_name)

    frontmatter = f"""---
title: "{title}"
tags: [{category}, wiki]
source: {url}
author: Top Heroes Wiki
category: {category}
---"""

    full_content = f"{frontmatter}\n\n# {title}\n\n{content_md}\n"
    return slug, full_content


def main():
    os.makedirs(KNOWLEDGEBASE_DIR, exist_ok=True)

    total = len(PAGES)
    success = 0
    for i, page_name in enumerate(PAGES, 1):
        print(f"[{i}/{total}] Crawling {page_name}...")
        result = crawl_page(page_name)
        if result:
            slug, content = result
            folder = os.path.join(KNOWLEDGEBASE_DIR, slug)
            os.makedirs(folder, exist_ok=True)
            filepath = os.path.join(folder, "KNOWLEDGE.md")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            success += 1
            print(f"  OK -> {filepath}")
        time.sleep(0.5)

    print(f"\nDone! {success}/{total} pages crawled.")


if __name__ == "__main__":
    main()
