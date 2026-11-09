# Beats: Narratives & Models

A static website for beats.itihasa.co. Python 3 builds the site with only its standard library:

```sh
python3 build.py
```

The complete published site is written to `site/`, an ignored build artifact. Source files are the truth.
Each essay is one JSON metadata file plus one HTML file in `articles/`; the JSON's `html_file` identifies its HTML file. Follow an existing pair's metadata structure and use a unique `slug`.
`articles/work.json` and `articles/reading.json` hold the Work and Reading sections. Local images are in `site-assets/`. External image URLs are intentional.

The builder also generates `404.html` using the existing stylesheet and page components. Existing design, templates, copy, and scripts are preserved.

## Publish updates

Add an essay pair, commit, then run `git push origin main`. GitHub Actions builds and deploys `site/` to Netlify on every push to `main`. The workflow can also be run manually from GitHub's Actions tab.

One-time setup: create a Netlify project and add these repository secrets under **Settings → Secrets and variables → Actions → New repository secret**:

- `NETLIFY_AUTH_TOKEN`: a Netlify personal access token created under Netlify user settings → Applications → Personal access tokens. Do not commit it or paste it into chat.
- `NETLIFY_SITE_ID`: the new project's Project ID (formerly Site ID), found in Netlify Project configuration → General → Project details.

Netlify's build command is `python3 build.py`; publish directory is `site` (configured in `netlify.toml`). GitHub Actions is the deployment owner; avoid also enabling Netlify's automatic Git builds, which would duplicate deployments. Node and Netlify CLI are deployment tools only; no JavaScript framework or bundler is used by the site.

## Domain cutover

1. Deploy and verify the new `https://<assigned-project-name>.netlify.app` address while Bolt and current DNS remain active.
2. Add `beats.itihasa.co` in the new Netlify project's Domain management. Preserve the old DNS values for rollback.
3. At the DNS provider for `itihasa.co`, replace the existing record for **beats** with a **CNAME** pointing to the exact assigned **<assigned-project-name>.netlify.app** hostname (no scheme or path). Remove conflicting A/AAAA/CNAME records at that same host only. Do not change the apex or nameservers.
4. Wait for DNS propagation, verify Netlify's HTTPS certificate status and open `https://beats.itihasa.co`. Keep Bolt running until the new domain, certificate, and page checks pass. Roll back to the saved DNS values if necessary.

The exact CNAME target cannot be supplied until Netlify creates the project. No A record is needed for this subdomain setup.
