# deepanshukandpal.com

Stories by Deepanshu Kandpal. Hugo site served at **https://deepanshukandpal.com**.

## Writing flow

Stories are written in the Obsidian vault (`Fiction/`), one note per story, with
`title`, `genre` and `hook` in the note's frontmatter. They're copied in with:

```sh
scripts/from_vault.py "/home/dk/vaults/Fiction/<story>.md"            # update as a draft
scripts/from_vault.py "/home/dk/vaults/Fiction/<story>.md" --publish  # make it live
```

`%% … %%` comments are dropped, `![[images]]` are copied in, `[[links]]` become text.

## Local preview

```sh
hugo server -D
```

## Deploy

Every push to `main` builds with Hugo 0.167 and deploys via GitHub Actions. The custom
domain is set in the repo's Pages settings; DNS is on Cloudflare (proxied).
