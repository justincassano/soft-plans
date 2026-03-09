# Soft Plans — Design System

## Philosophy

Soft Plans is a calm, intentional app designed for sensory-aware individuals. It suggests activities based on how much time you have, how you feel, and what you need. The design reflects a low-tech permacomputing ethos: quiet, minimal, no visual noise.

Think: terminal meets zine. No rounded corners, no gradients, no shadows, no animations. Every element earns its place.


## Colors

| Token | Value     | Usage                                      |
|-------|-----------|--------------------------------------------|
| BG    | `#FFFBED` | Page background (warm cream)               |
| Main  | `#000000` | Text, borders, icons                       |
| Meta  | `#0000EE` | Links, interactive timestamps, active items|
| Nav   | `#FCF3CC` | Button fills, dropdown backgrounds         |
| Muted | `#6D6D6C` | Quotes, completed/struck-through items     |


## Typography

Font: **Figtree** throughout. No other fonts. Figtree is a Google Font — load via Google Fonts API.

| Token  | Weight | Size | Letter Spacing | Usage                          |
|--------|--------|------|----------------|--------------------------------|
| Header | 700    | 16px | 0.64px         | "Soft Plans" wordmark, section headers like "INPUT" |
| Body   | 500    | 16px | 0.64px         | Form labels, activity suggestions, dropdown items   |
| Sub    | 500    | 14px | 0.56px         | Timestamps, quotes, secondary info                  |

Line height is normal/auto across all type. The wide letter-spacing is important — it gives the type room to breathe and contributes to the calm, unhurried feel.

Load: `<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@500;700&display=swap" rel="stylesheet">`

Fallback stack: `"Figtree", system-ui, -apple-system, sans-serif`


## Layout

- Mobile-first: designed at **375px** width
- Content padding: **20px** from screen edges
- Inner content left margin: **37px** from screen edge (17px from content box edge)
- Max content width within bordered areas: **335px**


## Components

### Header Bar
- "Soft Plans" in Header type, top-left at `(20px, 36px)`
- Hamburger icon top-right at `(339px, 37px)` — three horizontal lines, 16px wide, 1.5px stroke
- Full-width horizontal rule at **82.5px** from top, 1.5px black stroke, extends edge to edge

### Hamburger Dropdown
- Background: Nav (`#FCF3CC`)
- Border: 1.5px solid black
- Width: ~141px, anchored to top-right
- Items in Body type: "Choose...", "Home", "History", "Account"
- Small downward chevron arrow beside "Choose..."

### Form Card (Home Screen)
- Bordered box: 1.5px solid black, 335px wide
- Title row: "Your current state" in Body type, inside a 50px-tall bordered header strip
- Four input sections stacked vertically, each with:
  - Label in Body type (e.g., "Time available:", "Energy level:", "Emotional state:", "Desired Focus:")
  - "Choose..." dropdown below each label

### Dropdowns
- Default state: bordered box, 1.5px black, ~145px wide, 32px tall
- Label "Choose..." in Body type with small downward chevron on right
- Open state: Nav (`#FCF3CC`) background, bordered, items listed vertically in Body type
- Time options: "5 minutes", "30 minutes", "1 hour", "2 hours", "Half day", "Full day"

### Generate Button
- Default: bordered box, 1.5px black, no fill, text "Generate" in Body type
- Loading state: Nav fill (`#FCF3CC`), text "Generating..."
- Width adapts to content (~104px default, ~157px loading)

### Results Card
- Same bordered box style as form card, 335px wide
- Header strip with timestamp in Sub type, Meta color (`#0000EE`), clickable
- "INPUT" subheader in Body type, indented
- Input summary: "Time: Full day", "Energy: Good", etc. in Body type
- Activity suggestions as checklist:
  - Unchecked: 12px square, 1.5px border in Muted (`#6D6D6C`), text in Body type
  - Checked: 12px square, filled Meta (`#0000EE`), text struck through in Muted
- Quote at bottom in Sub type, Muted color

### History List
- Stack of collapsible bordered rows, each 50px tall, 335px wide
- Timestamp in Sub type, Meta color
- Expanded row shows full results card content

### Onboarding
- Username field: bordered input, 335px wide, 50px tall
- Password field: same style
- Submit button: same as Generate button
- Error state: solid black background, cream text (e.g., "Username Taken")

### Account Page
- Simple stacked list of labeled fields
- Labels in Sub type: "Username:", "Email:", "Password:", "Account:"
- Values in Sub type below each label
- Action links in Sub type, Meta color: "Change name", "Change email", "Change password", "Close account"

### About Page
- Body text in Sub type, left-aligned, 248px max width
- Paragraph breaks between sections


## Interaction States

- **Links/interactive text:** Meta color (`#0000EE`), no underline by default
- **Completed items:** struck through, Muted color, filled blue checkbox
- **Error states:** inverted — black background, cream text
- **Loading:** Nav-colored fill on button, "Generating..." text
- **Dropdowns:** expand in place with Nav background


## Borders

Everything uses the same border: **1.5px solid black**. No variation. No rounded corners. No shadows. This consistency is the aesthetic.


## Dropdown Option Values

### Time Available
5 minutes, 30 minutes, 1 hour, 2 hours, Half day, Full day

### Energy Level
Very low, Low, Okay, Good, High

### Emotional State
Sad, Anxious, Overwhelmed, Bored, Neutral, Content, Happy, Excited

### Desired Focus
Rest, Movement, Creativity, Connection, Maintenance, Exploration, Reflection


## Glyphs (Planned)

A library of small monochrome illustrations is planned — simple, icon-like drawings (e.g., snake, cloud, mountain, flower, butterfly, star, fish, campfire, etc.) that will appear on history cards as a visual shorthand related to the generated activities. These are not yet implemented. When they are, they should feel hand-drawn, quiet, and consistent with the minimal aesthetic. Each history row has a small square placeholder on the right side for a glyph.


## Future Features (Not Yet Built)

- Share feature (share a generated plan)
- Pattern recognition (surface trends in user behavior over time)
- Like/favorite activities
- Notes on activities
- Activity grouping by category (cooking, nature, crafts, etc.) with cross-recommendations


## What This Is Not

- No gradients
- No border-radius
- No box-shadows
- No hover color changes
- No transition animations
- No icons beyond the hamburger (until glyphs are implemented)
- No decorative elements

The restraint is the design.
