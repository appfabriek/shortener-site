# Publish template → Dok domain

Push HTML/CSS/JS/images from a **template GitHub repo** into a domain (custom mode).

Same direction as book publish: **repo → Action → API**, no domain GitHub PAT on the server.

## Setup

No secret. The domain is bound to the repo (`Domain#template_repo`, set by a data
migration for the repos in `docs/features/domain-templates.md`); dok accepts the
job's GitHub Actions ID token from that repo (dok#884). On production only
`main` publishes; staging and accept also take a branch.

1. Vendor this action into the site repo as `.github/actions/publish-template/`.
2. Add a workflow with `permissions: id-token: write`. The action publishes to
   `staging.<host>`, `accept.<host>` and `<host>` in that order and checks each
   home page; a failure stops the rest.

```yaml
# .github/workflows/publish-template.yml
name: Publish template to dok
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  id-token: write
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/publish-template
        with:
          host: liveplaylists.com
```

`environments` picks fewer (`staging` to try a branch). A `token` (`dtt_…`)
still works and publishes to `host` only.

`/robots.txt` is owned by Rails (`User-agent: *` + `Allow: /`, on staging and accept `Disallow: /`). The action no
longer ships a template `robots.txt`; the publish API ignores that filename so a
`Disallow: /` in a theme repo cannot override the platform policy.

A published root `llms.txt` is served at `GET /llms.txt` (Rails, `text/plain`).
Without that file the platform default is used. The app does not ship
`public/llms.txt`, so a static file cannot shadow the template.

Universal-link files are part of the default path set:
`.well-known/apple-app-site-association` and `.well-known/assetlinks.json`.
The publish API allows only those two names under `.well-known/`. Leading-dot
directories are preserved (do not `lstrip("./")` the relative path).

Optional `invite/index.html` (and `invite/index.{locale}.html`) is a soft
landing for Universal Links such as `/invite/<token>`, `/i/<code>` and
`/r/<code>`. Publish that one file; do not generate per-token HTML. Rails
serves it for every `/invite/*`, `/i/*` and `/r/*` path. AASA on the domain
should include `/invite/*`, `/i/*` and `/r/*` (landing-repo publish; clink
owns Coachlink AASA).

Every host needs a Domain row on staging and accept too (`bin/accept-sync` copies
them from production). A missing one fails the run before production.

## Local

```bash
BVG_HOST=accept.example.com BVG_TOKEN=dtt_... \
  bash .github/actions/publish-template/publish.sh
# In a template repo (after vendoring):
#   bash .github/actions/publish-template/publish.sh
```
