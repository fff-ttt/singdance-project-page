# SingDance Project Page

Static project page for **SingDance: Compositional Zero-Shot Singing-and-Dancing Video Generation with Role-Aware Audio Conditioning**.

## Repository layout

- `site/` is the optimized public site deployed to GitHub Pages.
- `scripts/validate_site.py` checks local references, anchors, duplicate IDs,
  accidental source clips, absolute local paths, and GitHub's per-file limit.
- The root-level `index.html` and `assets/` directory are local authoring masters
  and are intentionally ignored by Git.

## Local preview

```bash
python -m http.server 8000 --directory site
```

Open <http://localhost:8000> and run the release checks with:

```bash
python scripts/validate_site.py site
```

## GitHub Pages deployment

The workflow in `.github/workflows/deploy-pages.yml` validates and deploys
`site/` whenever `main` is updated. In the GitHub repository, open
**Settings → Pages** and set **Source** to **GitHub Actions** once.

The resulting project-site URL is normally:

```text
https://YOUR-GITHUB-USER.github.io/YOUR-REPOSITORY/
```

## Media notice

Some source media originate from publicly available online content and are used
solely for non-commercial academic research. Rights remain with their respective
owners. No license is granted for third-party media assets.
