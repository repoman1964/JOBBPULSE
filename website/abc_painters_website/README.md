# ABC Painters — website

Standalone marketing site for **ABC Painters**, a residential interior/exterior painting company in Acworth, Georgia.

Built from the Trusted Local Trade visual system (navy + safety orange) used in the Grok Builder home-services templates. There was no painter prompt in that library; this site is the painter adaptation.

## Stack

- Nuxt 4 / Vue 3 (SSR)
- Static content (no JobbPulse API)

## Routes

| Area | Path |
|---|---|
| Home | `/` |
| Services | `/services`, `/services/interior-painting`, `/services/exterior-painting`, `/services/cabinets-and-trim` |
| Portfolio | `/portfolio` |
| Service areas (3 cities only) | `/service-areas`, `/service-areas/acworth`, `/kennesaw`, `/cartersville` |
| About, FAQ, contact | `/about`, `/faq`, `/contact` |
| Legal | `/privacy`, `/terms` |

Demo contact:

- Phone: `(555) 123-4567`
- Email: `painter@abcpainters.com`
- Address: `4321 Northeast Flanders, Acworth, GA 30101`

## Quick start

```bash
cd abc_painters_website
make install
make dev
# → http://localhost:3003
```
