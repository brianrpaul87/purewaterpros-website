# Pure Water Pros Website Checkpoint

**Hard-saved:** July 10, 2026

## Repository and branches

- Repository: `brianrpaul87/purewaterpros-website`
- `main`: imported copy of the current GreenGeeks website
- `redesign`: active pre-launch redesign branch
- The GreenGeeks live website has not been changed by this redesign work.

## Business decisions locked in

- Pure Water Pros is not currently operating.
- Target opening: the third week of August 2026.
- Initial service area: Greater Victoria and the West Shore, British Columbia.
- The discontinued phone number `905-242-3846` must not appear in the redesign.
- No public service phone number is advertised before launch.
- The site must not imply same-day service, active emergency service, or confirmed appointment availability before launch.
- Primary pre-launch conversion: request an August follow-up by email/form.

## Redesign direction

- Clean, premium local-service presentation using light backgrounds, deep navy and aqua accents.
- Homeowner-first language rather than technician-note language.
- Clear pre-launch notices throughout the site.
- Real installation photography retained as a trust asset.
- Strong mobile-first layout.

## Water Problem Checker

A deterministic guided tool has been built into the pre-launch homepage. It is intentionally not marketed as a full AI diagnosis.

Purpose:

- educate the homeowner;
- identify a sensible next conversation;
- explain why testing and inspection matter before equipment selection;
- reassure the visitor that contacting Pure Water Pros is the logical next step;
- attach useful context to the lead form.

Current paths include:

- hardness/scale;
- iron or manganese staining;
- sulfur or unusual odour;
- chlorine/drinking-water concerns;
- sediment/cloudiness;
- weak pressure/flow;
- existing treatment not working;
- positive bacteria/safety concern;
- active leak/flooding/electrical risk.

Special logic includes:

- hot-water-only odour directs attention to the water heater/anode before whole-home sulfur treatment;
- existing treatment prompts raw-versus-treated testing and equipment identification;
- urgent health and flooding concerns are directed away from waiting for an August appointment.

The checker is educational only and does not confirm water safety or replace proper testing.

## Files changed on `redesign`

- `index.html`
- `assets/prelaunch.css`
- `assets/water-problem-checker.js`
- `contact.php`
- `contact.html`
- `thank-you.html`
- `.htaccess`
- `sitemap.xml`

## Contact and form behaviour

- Homepage form is labelled as a pre-launch follow-up request, not a confirmed appointment.
- Checker results can be attached to the form.
- PHP handler emails requests to `info@purewaterpros.ca`.
- Form includes a honeypot spam field and basic validation.
- Thank-you page repeats that the submission is not a confirmed appointment.

## Pre-launch routing and SEO

- `.htaccess` temporarily redirects old public pages to the pre-launch homepage while allowing assets, images, form submission and the thank-you page.
- The sitemap contains only the homepage during pre-launch.
- Structured data describes an organization preparing to open, not an active local business.

## Next website steps

1. Create a visual preview of the `redesign` branch.
2. Review desktop and mobile presentation.
3. Confirm final wording, service area and launch date.
4. Confirm which replacement phone number, if any, should be published at launch.
5. Deploy to GreenGeeks only after approval.
6. Later expand the pre-launch page into the full service website while preserving the checker.

## Current status

Website work is parked here so development can return to Water Copilot Pro.
