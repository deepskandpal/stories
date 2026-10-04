# deepanshukandpal.com

Deepanshu Kandpal's own site, and the root of everything else. Hugo, served at **https://deepanshukandpal.com**.

Two sections:

- **Thoughts** (`content/thoughts/`): opinion pieces, at `/thoughts/<slug>/`.
- **Writings** (`content/writings/`): evidence-led pieces, at `/writings/<slug>/`. A tech piece's home is
  404engineernotfound.com; its copy here carries `canonical:` pointing there.

The tech work lives at https://404engineernotfound.com (linked as "Tech" in the header).

## Writing flow

Pieces are written in the Obsidian vault (`/home/dk/vaults/deepanshu-kandpal/deepanshukandpal.com/`) and copied in with:

```sh
scripts/from_vault.py "<note>.md" --section thoughts            # update as a draft
scripts/from_vault.py "<note>.md" --section writings --publish  # make it live, dated today
```

`%% … %%` comments are dropped, `![[images]]` are copied in, `[[links]]` become text. Optional note
frontmatter: `title`, `tags`, `description`, `canonical`.

The line under the name on the home page is `params.homeline` in `hugo.toml` (empty = no line).

## Local preview

```sh
hugo server -D
```

## Deploy

Every push to `main` builds with Hugo 0.167 and deploys via GitHub Actions. The custom
domain is set in the repo's Pages settings; DNS is on Cloudflare (proxied).

## Look

[Tufte CSS](https://edwardtufte.github.io/tufte-css/) (MIT, vendored in `static/tufte/` with the ET Book fonts), plus a few overrides in `assets/css/main.css`. Since 04 Oct 2026 the design is frozen until the end of Q4.

Margin notes in a piece:
- `{{< sidenote >}}a numbered note{{< /sidenote >}}`
- `{{< marginnote >}}an unnumbered note{{< /marginnote >}}`

On a phone, both tuck behind a tap.
