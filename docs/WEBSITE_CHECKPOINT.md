# Pure Water Pros Website Checkpoint

**Updated:** September 1, 2026

## Repository and deployment

- Repository: `brianrpaul87/purewaterpros-website`
- Production branch: `main`
- Live hosting: GreenGeeks
- GitHub does **not** automatically deploy to GreenGeeks; production files must be uploaded to the site hosting account.

## Current business state

Pure Water Pros entered a **soft launch on September 1, 2026**.

Public website language should now reflect an operating business that is accepting inquiries and booking a limited number of September appointments. It should no longer describe Pure Water Pros as "pre-launch," "preparing to open," or waiting for scheduling to begin.

The business should not imply same-day or emergency-response availability unless that capability is intentionally added later.

## Current homepage position

The homepage now:

- says Pure Water Pros is **now booking September appointments**;
- accepts service requests rather than pre-launch requests;
- keeps the Water Problem Checker;
- emphasizes reverse osmosis and existing-equipment service for the initial launch period;
- keeps broader whole-home and advanced treatment services available for assessment/quotation;
- retains the published phone number `778-400-1267` and `info@purewaterpros.ca`;
- preserves the existing Greater Victoria / West Shore SEO structure and service pages.

## Water Problem Checker

The deterministic guided Water Problem Checker remains on the homepage. It is educational and does not confirm water safety or replace proper testing.

Current paths include hardness/scale, iron or manganese staining, sulfur/odour, chlorine/drinking-water concerns, sediment/cloudiness, weak pressure/flow, existing treatment not working, bacteria/safety concerns, and leak/flooding/electrical risks.

## Contact flow

- Homepage form is now a service-request form.
- `contact.php` emails requests to `info@purewaterpros.ca`.
- Checker results can be attached to the request.
- The form includes a honeypot spam field and validation.
- `thank-you.html` now confirms receipt of a service request without pre-launch language.
- `contact.html` redirects visitors to the homepage service-request section.

## Files required for the September 1 GreenGeeks update

Upload/replace these files in the Pure Water Pros web root:

1. `index.html`
2. `contact.php`
3. `contact.html`
4. `thank-you.html`

No CSS, JavaScript, image, sitemap, or `.htaccess` replacement is required for this specific soft-launch copy update.

## Current status

The GitHub `main` branch is the authoritative September 1, 2026 soft-launch version. GreenGeeks must be manually updated with the four production files listed above.
