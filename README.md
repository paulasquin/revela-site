# revela.aidiligence.eu

Support page, terms and privacy policy of the Revela Android app (published by Guardia SAS).

The texts are written in the Revela repository (`docs/play/conditions.md`,
`docs/play/privacy-policy.md`); this repository only publishes them. Blockquotes in those files are
editorial notes and are left out. After changing a text there:

```bash
uv run --with markdown python tools/build.py ../../revela
```

Preview: `python3 -m http.server 8791`, then <http://localhost:8791>.

Deployment: GitHub Pages, `main` branch, repository root; the domain is declared by `CNAME`.
DNS (OVH, zone `aidiligence.eu`): `revela CNAME paulasquin.github.io.`

| URL | Content |
|---|---|
| `/` | Support page (contact, subscription, links) |
| `/conditions/` | Conditions d'utilisation et d'abonnement |
| `/confidentialite/` | Privacy policy (FR + EN) |
| `/privacy/` | Redirect to `/confidentialite/` |
