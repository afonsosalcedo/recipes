#!/usr/bin/env python3
"""Build HomeView-ready recipe pages.

Each recipe is one JSON file in _recipes/<slug>.json.
A photo is optional: put it at <slug>/photo.jpg and rebuild.
Run: python3 build.py
"""
import html, json, pathlib

BASE = "https://afonsosalcedo.github.io/recipes"
ROOT = pathlib.Path(__file__).parent
CSS = """
:root{--ink:#2a2420;--muted:#7a6e64;--accent:#a8432a;--bg:#fbf7f2;--card:#fff;--line:#eadfd3}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.55 -apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif}
main{max-width:820px;margin:0 auto;padding:28px 22px 60px}
h1{font-family:Georgia,"Times New Roman",serif;font-size:2rem;line-height:1.15;margin:0 0 8px}
.hero{width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:16px;margin-bottom:20px}
.lede{color:var(--muted);margin:0 0 16px}.meta{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:28px}
.meta span{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:.9rem}
h2{font-size:1.1rem;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);margin:32px 0 12px}
ul.ing{list-style:none;padding:0;margin:0;background:var(--card);border:1px solid var(--line);border-radius:14px}
ul.ing li{padding:10px 16px;border-bottom:1px solid var(--line)}ul.ing li:last-child{border-bottom:0}
ol.steps{list-style:none;counter-reset:s;padding:0;margin:0}
ol.steps li{counter-increment:s;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px 16px 64px;margin-bottom:12px;position:relative}
ol.steps li::before{content:counter(s);position:absolute;left:18px;top:14px;width:32px;height:32px;border-radius:50%;background:var(--accent);color:#fff;font-weight:600;display:flex;align-items:center;justify-content:center}
ol.steps strong{display:block;margin-bottom:2px}.notes{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 18px}
.list a{display:flex;gap:16px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:12px;color:inherit;text-decoration:none}
.list img,.list .ph{width:96px;height:72px;object-fit:cover;border-radius:10px;background:var(--line);flex:none}
"""
e = html.escape


def mins(iso):
    h = m = 0
    s = iso.replace("PT", "")
    if "H" in s:
        h, s = s.split("H")
        h = int(h)
    if s.endswith("M"):
        m = int(s[:-1])
    return h * 60 + m


def build(r):
    slug = r["slug"]
    photo = ROOT / slug / "photo.jpg"
    total = mins(r["prepTime"]) + mins(r["cookTime"])
    ld = {
        "@context": "https://schema.org", "@type": "Recipe",
        "name": r["name"], "description": r["description"],
        "author": {"@type": "Person", "name": "Hideaway House Kitchen"},
        "recipeYield": r["yield"], "prepTime": r["prepTime"], "cookTime": r["cookTime"],
        "totalTime": f"PT{total}M", "recipeCuisine": r.get("cuisine", ""),
        "suitableForDiet": "https://schema.org/VegetarianDiet",
        "recipeIngredient": r["ingredients"],
        "recipeInstructions": [{"@type": "HowToStep", "name": n, "text": t} for n, t in r["steps"]],
    }
    if r.get("protein"):
        ld["nutrition"] = {"@type": "NutritionInformation", "proteinContent": r["protein"]}
    if photo.exists():
        ld["image"] = [f"{BASE}/{slug}/photo.jpg"]
    chips = [r["yield"]]
    if r.get("protein"):
        chips.append(f"About {r['protein']} protein per serving")
    chips += [f"Prep {mins(r['prepTime'])} min", f"Cook {mins(r['cookTime'])} min"] + r.get("tags", [])
    out = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(r['name'])}</title><meta name="description" content="{e(r['description'])}">
{f'<meta property="og:image" content="{BASE}/{slug}/photo.jpg">' if photo.exists() else ''}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, indent=1)}</script>
<style>{CSS}</style></head><body><main>
{f'<img class="hero" src="photo.jpg" alt="{e(r["name"])}">' if photo.exists() else ''}
<h1>{e(r['name'])}</h1><p class="lede">{e(r['description'])}</p>
<div class="meta">{''.join(f'<span>{e(c)}</span>' for c in chips)}</div>
<h2>Ingredients</h2><ul class="ing">{''.join(f'<li>{e(i)}</li>' for i in r['ingredients'])}</ul>
<h2>Steps</h2><ol class="steps">{''.join(f'<li><strong>{e(n)}</strong>{e(t)}</li>' for n, t in r['steps'])}</ol>
{('<h2>Notes</h2><div class="notes">' + ''.join(f'<p>{e(n)}</p>' for n in r['notes']) + '</div>') if r.get('notes') else ''}
<p><a href="../">All recipes</a></p>
</main></body></html>
"""
    (ROOT / slug).mkdir(exist_ok=True)
    (ROOT / slug / "index.html").write_text(out)
    return slug, r["name"], photo.exists()


def main():
    items = [build(json.loads(p.read_text())) for p in sorted((ROOT / "_recipes").glob("*.json"))]
    links = "".join(
        f'<a href="{s}/">' + (f'<img src="{s}/photo.jpg" alt="">' if ph else '<span class="ph"></span>') + f'<span>{e(n)}</span></a>'
        for s, n, ph in sorted(items, key=lambda x: x[1]))
    (ROOT / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hideaway House Recipes</title><style>{CSS}</style></head><body><main>
<h1>Hideaway House Recipes</h1><div class="list">{links}</div></main></body></html>
""")
    print("built", [s for s, _, _ in items])


if __name__ == "__main__":
    main()
