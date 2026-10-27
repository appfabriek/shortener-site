# dok — Shortener template

Bitly-style URL forwarder template for [dok](https://github.com/appfabriek/dok) domains.

In use on **geert.link** and **nm.nu** (shorteners, with the admin shell) and on **koek.in**, **dox.onl** and **knst.link** (only the bare home).

## What it does

- **Public landing**: a bare page per domain (board "Korte links"): the name, one line on what the links are, "Mail me" and a small sign-in link. Built by `scripts/build-bare.py` into `index.html` and `hosts/<host>/index.html`
- **Admin chrome**: clean dark dashboard with `Links` + `Settings` nav, auto-redirects logged-in admins to `/admin/links`
- **Non-admin lockout**: regular users who sign in see a "nothing here for you" card with a logout button — no nav, no access

Authorization is enforced by dok (`user.admin?`). This template just renders accordingly.

## How to use this template

1. Fork (or *Use this template*) on GitHub.
2. Bind the repo to your domain in dok (`Domain#template_repo`, a data migration; dok#884). No secret: the job's GitHub ID token proves the repo.
3. Push to `main` — the Action publishes a full snapshot to `POST /api/v1/template/publish` on `staging.<host>`, `accept.<host>` and `<host>`.

There is no pull/sync and no “Sync now”. The old webhook (`/webhooks/github/assets`) returns 410.

## Files

| File             | Purpose                                                |
|------------------|--------------------------------------------------------|
| `index.html`     | Bare home for geert.link + the admin console, built by `scripts/build-bare.py` |
| `hosts/<host>/index.html` | Bare home per domain; the workflow copies `hosts/<host>/` over the tree |
| `css/bare.css`, `fonts/` | Bare home styling, JetBrains Mono (OFL) |
| `app.html`       | Logged-in shell (wraps every authenticated page)       |
| `css/landing.css`| Styling for the public landing                         |
| `css/app.css`    | Styling for the logged-in shell + Rails content        |
| `images/`        | Logo/favicon served by TemplateServer (`/images/*`)    |
| `hosts/<host>/images/` | A host's own icon (`logo.png`, `apple-touch.png`): geert.link's mark; koek.in, dox.onl and knst.link have the Appfabriek icon, since the bare design has no mark |
| `icons/`         | Extra icon pack (not served unless published under `images/`) |
| `.github/workflows/publish-template.yml` | Push snapshot to dok |
| `.github/actions/publish-template/` | Composite action + `publish.sh` |

## Placeholders

Used in `index.html` (public):

| Placeholder        | What it becomes                                           |
|--------------------|-----------------------------------------------------------|
| `{{login_form}}`   | Full OAuth + magic-link login form (with built-in styling) |
| `{{login_button}}` | Single primary OAuth button                                |
| `{{footer}}`       | dok footer                                            |
| `{{csrf_meta}}`    | CSRF meta tags                                             |
| `{{brand_name}}`   | Your domain's brand name                                   |
| `{{brand_logo}}`   | `/images/logo.png` from this tree, else `/logokl.svg` |
| `{{brand_apple_touch_icon}}` | `/images/apple-touch.png` from this tree, else `/icon.png` |
| `{{current_year}}` | Current year                                               |

Used in `app.html` (logged-in):

| Placeholder        | What it becomes                                           |
|--------------------|-----------------------------------------------------------|
| `{{content}}`      | The Rails-rendered page content                            |
| `{{flash}}`        | Toast container                                            |
| `{{user_menu}}`    | Email + logout button                                      |
| `{{user_role}}`    | `"admin"`, `"user"`, or `"guest"` — used for role gating  |
| `{{footer}}`       | dok footer                                            |
| `{{csrf_meta}}`    | CSRF meta tags                                             |
| `{{brand_name}}`   | Your domain's brand name                                   |
| `{{brand_logo}}`   | `/images/logo.png` from this tree, else `/logokl.svg` |
| `{{brand_apple_touch_icon}}` | `/images/apple-touch.png` from this tree, else `/icon.png` |
| `{{page_title}}`   | Current page title                                         |
| `{{current_year}}` | Current year                                               |

## Role-based UI

The shell uses `<body data-role="{{user_role}}">` plus CSS to gate the admin chrome:

- `body[data-role="user"] .admin-only { display: none }` — hides nav and content
- `body[data-role="user"] .user-empty { display: flex }` — shows the lockout card

No JavaScript, no Rails changes. Authorization is still enforced by dok; this is purely cosmetic.

## Publish on push

The repo ships with `.github/workflows/publish-template.yml`. This one tree publishes to geert.link, nm.nu, koek.in, dox.onl and knst.link, each first on `staging.` and `accept.`. No secrets: the job's GitHub ID token proves this repo (dok#884).

Local, with a `dtt_` token of one host (do not log it):

```bash
BVG_HOST=accept.geert.link BVG_TOKEN=dtt_... \
  bash .github/actions/publish-template/publish.sh
```

## Customizing for your domain

The defaults are intentionally generic. Tweak:

- **Colors**: edit `--accent` and `--accent-2` in both CSS files.
- **Demo slugs**: edit the `.demo-card` rows in `index.html` to match your actual top links.
- **Copy**: rewrite the hero and feature sections — make it feel like your team.
- **Logo**: put `images/logo.png` (and optionally `images/apple-touch.png`) in this repo. `{{brand_logo}}` points at that file. There is no logo upload on the Domain record.
  The shared default is the neutral arrow mark (`brand/shortener-mark.svg`).
  A host gets its own mark via `hosts/<host>/images/*`, copied over the tree
  by the publish workflow (geert.link: `brand/geert-link-mark.svg`).
  Regenerate PNGs/ICO from the SVGs with `rsvg-convert` + `magick`.

## Docs

- [Domain templates](https://github.com/appfabriek/dok/blob/main/docs/features/domain-templates.md)
- [Custom landing pages & app shell](https://github.com/appfabriek/dok/blob/main/docs/features/custom-landing-pages.md)
