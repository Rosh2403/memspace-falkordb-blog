# Memspace blog

The engineering blog for [Memspace](https://github.com/pranavjana/shared-memory-mcp): one memory that Dot, Muse, Grok Bot and other MCP assistants share, built on an ontology and FalkorDB for Graph Hacks.

Live at https://memspace-falkordb-blog.vercel.app

| Page | What it covers |
|---|---|
| `/` (`index.html`) | The story: setup, Dot and Muse sharing memory, a shared space with Grok Bot, the ontology, FalkorDB, and what we learned |
| `/ontology` (`ontology.html`) | Schema 1.2.0 reference: the rules, how a note becomes facts, all 13 types and 49 relationships, sharing, growing the schema |
| `/falkordb` (`falkordb.html`) | The Cypher queries, query plans, in-graph search, the job queue, and what bit us |

## Stack

Static HTML, one stylesheet (`styles.css`) and one small script (`app.js`) with no build step and no framework. Every page reads fine with JavaScript off; the script only adds the click-to-load video, the section dots, reading progress and Cypher highlighting. Fonts are Geist and Geist Mono from Google Fonts, the same as the Memspace dashboard.

Diagrams are inline SVG or HTML, drawn for this site. Screenshots in `assets/img/` come from the real Memspace dashboard (demo account) and FalkorDB Browser running the repo's sample graph.

## Preview locally

```bash
npx serve@14.2.4 -l 4321 .
```

Then open http://localhost:4321. `serve.json` turns on clean URLs so `/ontology` works the same as on Vercel.

## Updating the ontology catalog

The type and relationship tables on `/ontology` are generated from an export of the live schema (`src/ontology.ts` in the Memspace repo), stored in `data/`:

```bash
python3 scripts/build-catalog.py data/ontology-1.2.0.json
```

It rewrites only the blocks between `<!-- catalog:NAME:start -->` and `<!-- catalog:NAME:end -->`, and fails if a relationship is missing from the reader-facing groups.

## Share image

`assets/og.png` is a screenshot of `scripts/og.html`. With the local preview running:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
  --window-size=1200,630 --screenshot="$PWD/assets/og.png" http://localhost:4321/scripts/og
```

## Deployment

Vercel serves the repository root as a static site. `vercel.json` sets clean URLs, cache headers and a content security policy, and `.vercelignore` keeps `scripts/` and `data/` out of the deploy. The current Vercel project was uploaded directly and isn't linked to this repository yet; once it is, pushes to `main` deploy automatically. Until then, redeploy from the Vercel dashboard or with `vercel --prod`.
