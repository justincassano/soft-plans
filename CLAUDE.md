# Soft Plans

Soft Plans is a calm activity suggestion app. You tell it how much time you have, your energy level, your mood, and what kind of focus you want — and it generates a short list of activities with a quote. Designed for sensory-aware individuals, rooted in a low-tech permacomputing ethos.

By Justin Cassano.


## Stack

- **Backend:** Python / Flask
- **Frontend:** Jinja2 templates + static CSS/JS
- **Data:** JSON files (`quotes.json`, `Soft_Plans_Activity_Suggestions.json`)
- **Target platform:** PWA (Progressive Web App) — mobile-first at 375px, installable to home screen


## Key Files

- `app.py` — Flask routes and application logic
- `models.py` — Data models
- `main.py` — Entry point
- `templates/` — Jinja2 HTML templates
- `quotes.json` — Quote database (quote text + attribution)
- `Soft_Plans_Activity_Suggestions.json` — Activity database organized by time/energy/mood/focus
- `DESIGN.md` — Complete visual design system (colors, typography, components, spacing). **Read this before making any UI changes.**


## App Flow

1. **Onboarding:** User creates account (username + password)
2. **Home:** User selects current state via four dropdowns (time, energy, mood, focus) → hits Generate
3. **Results:** App returns ~4 activity suggestions + a quote, displayed as a checklist. User can check off completed activities.
4. **History:** Past generations are saved and browsable, each as a collapsible card with timestamp
5. **Navigation:** Hamburger menu → Home, History, Account
6. **Account:** View/change username, email, password; close account
7. **About:** Brief description of the app and its philosophy


## Design Principles

Read `DESIGN.md` for the full spec. The essential rules:

- **Font:** Figtree (Google Font), weights 500 and 700 only
- **Colors:** Cream background (#FFFBED), black text/borders, blue links (#0000EE), warm yellow for interactive fills (#FCF3CC)
- **Borders:** 1.5px solid black everywhere. No border-radius. No shadows.
- **Spacing:** 20px page padding, generous letter-spacing (0.64px body, 0.56px sub)
- **Restraint:** No gradients, no animations, no decorative elements. The app should feel quiet.


## What Not To Do

- Don't add CSS frameworks (no Tailwind, Bootstrap, etc.) — write plain CSS
- Don't add rounded corners or shadows to anything
- Don't use any font other than Figtree
- Don't introduce JavaScript frameworks — keep it vanilla JS + Jinja templates
- Don't over-engineer; this is a small, focused app
- Don't change the color palette without discussion
