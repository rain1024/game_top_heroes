# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a data repository for the mobile game **Top Heroes**. It contains structured hero data and individual hero profile pages. There is no build system, test suite, or application code — it is purely a content/data project.

## Repository Structure

- `heroes_data.json` — Central data file containing all heroes (name, faction, rarity, wiki link) and game upgrade tables (star upgrades, tier upgrades, skill upgrade costs)
- `heroes/` — One markdown file per hero (e.g., `Knight.md`, `Rose_Princess.md`), each with faction, rarity, and wiki link
- `.mcp.json` — MCP server config (Chrome DevTools)

## Data Model

Heroes belong to one of three **factions**: League, Nature, Horde.

Heroes have one of four **rarities** (ascending): Rare, Epic, Legendary, Mythic.

## Conventions

- Hero markdown filenames use underscores for spaces (e.g., `Rose_Princess.md` for "Rose Princess")
- Each hero `.md` file follows a consistent format: H1 name, then bullet list of Faction, Rarity, and Wiki link
- The `heroes_data.json` must stay in sync with the individual hero markdown files
- Wiki URLs follow the pattern `https://topheroes1.fandom.com/wiki/{Name_With_Underscores}`

## Git

- Never include a `Co-Authored-By` line in commit messages
