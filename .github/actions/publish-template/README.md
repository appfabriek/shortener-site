# Publish template → dok domain

Push HTML/CSS/JS/images from a **template GitHub repo** into a domain (custom mode).

Same direction as book publish: **repo → Action → API**, no domain GitHub PAT on the server.

## Setup

1. Domain admin → **Admin → Settings → Template** → choose **Custom** → **Create publish token** (`dtt_…`).
2. Store the token as a repo secret, e.g. `BVG_TEMPLATE_TOKEN`.
3. Vendor this action into the template repo as `.github/actions/publish-template/`.
4. Add a workflow that targets the right **host** per environment:

```yaml
# .github/workflows/publish-template.yml
name: Publish template
on:
  push:
    branches: [main]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Publish to production
        uses: ./.github/actions/publish-template
        with:
          host: liveplaylists.com          # or accept.* / staging.*
          token: ${{ secrets.BVG_TEMPLATE_TOKEN }}
```

Use different secrets/hosts for accept, staging, and production (matrix or separate workflows).

## Local

```bash
BVG_HOST=accept.example.com BVG_TOKEN=dtt_... \
  bash .github/actions/publish-template/publish.sh
```
