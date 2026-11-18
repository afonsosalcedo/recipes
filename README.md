# Hideaway House Recipes

Recipe pages for Apple HomeView. Safari's "Start Cooking" view reads the schema.org Recipe JSON-LD on each page.

Live index: https://afonsosalcedo.github.io/recipes/

## Add a recipe
1. Add `_recipes/<slug>.json` (copy `_recipes/chili.json` for the format).
2. Optional photo: save it as `<slug>/photo.jpg` (landscape, about 1600 px wide).
3. Run `python3 build.py`, then commit and push. The page goes live at `https://afonsosalcedo.github.io/recipes/<slug>/` within a minute or two.

Write timings into step text ("simmer for 30 minutes") so HomeView can offer timers.
