(() => {
  const form = document.getElementById("water-checker-form");
  const resultPanel = document.getElementById("checker-result");
  const error = document.getElementById("checker-error");
  const titleEl = document.getElementById("result-title");
  const copyEl = document.getElementById("result-copy");
  const nextEl = document.getElementById("result-next");
  const attachButton = document.getElementById("attach-result");
  const restartButton = document.getElementById("restart-checker");
  const summaryInput = document.getElementById("diagnostic-summary");
  const messageInput = document.getElementById("request-message");
  const sourceSelect = document.getElementById("request-water-source");
  const attachedNote = document.getElementById("attached-note");
  const requestSection = document.getElementById("launch-request");
  const year = document.getElementById("year");

  if (year) year.textContent = String(new Date().getFullYear());
  if (!form || !resultPanel) return;

  const concernResults = {
    hardness: {
      title: "Hardness is possible, but sizing still matters.",
      copy: "Scale, spotting and poor soap performance are commonly associated with dissolved calcium and magnesium. The right softener size depends on measured hardness, household demand, iron content and available flow.",
      next: "Test the raw water and confirm peak flow before selecting or replacing a softener."
    },
    iron: {
      title: "Iron or manganese may be involved.",
      copy: "Orange or brown staining often points toward iron, while black or grey staining can involve manganese. Treatment depends on concentration, pH, oxygen demand, flow and whether the staining occurs before or after existing equipment.",
      next: "Arrange water testing and an equipment/site inspection before choosing media or an oxidation system."
    },
    odour: {
      title: "The source of the odour needs to be separated first.",
      copy: "A rotten-egg odour can come from hydrogen sulfide in the source water, biological activity, plumbing conditions or the water heater. Hot-only and whole-home odours follow different troubleshooting paths.",
      next: "Confirm whether the odour is hot-only, cold-only or present throughout the home, then test and inspect before selecting treatment."
    },
    chlorine: {
      title: "Taste and odour treatment should match the actual goal.",
      copy: "Municipal-water concerns may involve chlorine or chloramine taste, sediment, hardness or a drinking-water preference. Whole-home carbon and point-of-use reverse osmosis solve different problems and have different maintenance needs.",
      next: "Clarify whether the goal is every tap or drinking water only, then review local water conditions and plumbing demand."
    },
    sediment: {
      title: "Sediment treatment begins with identifying what is being captured.",
      copy: "Cloudiness, grit and plugged aerators can come from well sediment, disturbed plumbing, seasonal turbidity or failing treatment media. Installing a finer cartridge without checking flow can create pressure problems.",
      next: "Inspect the material, source and pressure loss, then size filtration around particle load and required flow."
    },
    pressure: {
      title: "Low pressure is not automatically a filtration problem.",
      copy: "Weak flow can involve a pump, pressure tank, clogged filter, undersized plumbing, exhausted media or a control-valve issue. Replacing treatment equipment before checking pressure and flow can miss the real cause.",
      next: "Measure pressure and flow at logical points in the system and inspect existing equipment before recommending changes."
    },
    equipment: {
      title: "An equipment inspection is the sensible first step.",
      copy: "Poor water after treatment can result from programming, bypass position, exhausted media, missed maintenance, a failed component or a change in raw water. The equipment label and current raw/treated readings are especially useful.",
      next: "Document the equipment make/model and compare raw versus treated water before deciding whether to repair, re-bed or replace it."
    },
    bacteria: {
      title: "A safety concern requires proper testing and public-health guidance.",
      copy: "A website checker cannot determine whether water is microbiologically safe. A positive E. coli result or boil-water notice should be treated as urgent and handled according to local public-health direction.",
      next: "Follow current public-health instructions now. After the immediate safety issue is addressed, a treatment professional can review the well, pretreatment and continuous disinfection options."
    },
    leak: {
      title: "An active leak or electrical risk should not wait for launch.",
      copy: "Water around electrical equipment, active flooding or a pressurized leak can damage property and create a safety hazard. Pure Water Pros is not currently operating an emergency-response service.",
      next: "Shut off water or power only when it is safe to do so, and contact an available emergency plumber, electrician or emergency service now."
    }
  };

  function selected(name) {
    return form.querySelector(`input[name="${name}"]:checked`)?.value || "";
  }

  function concernLabel(value) {
    const input = form.querySelector(`input[name="concern"][value="${value}"]`);
    return input?.nextElementSibling?.textContent?.trim() || value;
  }

  function buildSummary(data, result) {
    return [
      "Water Problem Checker summary",
      `Water source: ${data.source}`,
      `Primary concern: ${data.concernLabel}`,
      `Where noticed: ${data.location}`,
      `Existing treatment equipment: ${data.equipment}`,
      `Preliminary guidance: ${result.title}`,
      `Recommended next step: ${result.next}`
    ].join("\n");
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const source = selected("source");
    const concern = selected("concern");
    const location = selected("location");
    const equipment = selected("equipment");

    if (!source || !concern || !location || !equipment) {
      error.hidden = false;
      return;
    }

    error.hidden = true;
    const base = concernResults[concern];
    let copy = base.copy;
    let next = base.next;

    if (concern === "odour" && location === "Hot water only") {
      copy += " Because you selected hot water only, the water heater and anode should be investigated before assuming the source water needs whole-home sulfur treatment.";
      next = "Inspect the water heater/anode and compare a cold raw-water sample with the hot-water odour before proposing whole-home equipment.";
    }

    if (equipment === "Yes" && !["leak", "bacteria"].includes(concern)) {
      copy += " Since treatment is already installed, raw-versus-treated testing and the equipment model should be reviewed before recommending replacement.";
    }

    if (source === "Municipal water" && concern === "iron") {
      copy += " On municipal water, localized staining can also originate in building plumbing or a water heater, so the source should be confirmed before installing iron-removal equipment.";
    }

    const data = { source, concernLabel: concernLabel(concern), location, equipment };
    titleEl.textContent = base.title;
    copyEl.textContent = copy;
    nextEl.textContent = next;
    summaryInput.value = buildSummary(data, { title: base.title, next });
    resultPanel.dataset.source = source;
    form.hidden = true;
    resultPanel.hidden = false;
    resultPanel.focus();
  });

  attachButton.addEventListener("click", () => {
    const source = resultPanel.dataset.source;
    if (source && sourceSelect) sourceSelect.value = source;
    if (messageInput && !messageInput.value.trim()) {
      messageInput.value = "I completed the Water Problem Checker. My result is attached below.\n\n";
    }
    attachedNote.hidden = false;
    requestSection.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  restartButton.addEventListener("click", () => {
    form.reset();
    form.hidden = false;
    resultPanel.hidden = true;
    summaryInput.value = "";
    attachedNote.hidden = true;
    form.querySelector("input")?.focus();
  });
})();

(() => {
  const processSection = document.getElementById("process");
  const aboutSection = document.getElementById("about");
  if (!processSection || !aboutSection || document.getElementById("field-experience")) return;

  const style = document.createElement("style");
  style.textContent = `
    .field-experience-section{padding:72px 0;background:#f5f9fb}
    .field-experience-intro{max-width:760px;margin-bottom:26px}
    .field-experience-intro>p:not(.eyebrow){margin-bottom:0;color:var(--muted);font-size:17px}
    .field-experience-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
    .field-experience-card{margin:0;overflow:hidden;border:1px solid var(--line);border-radius:14px;background:#fff;box-shadow:0 8px 22px rgba(8,36,59,.06)}
    .field-experience-card picture{display:block;background:#eaf3f6}
    .field-experience-card img{display:block;width:100%;height:220px;object-fit:cover;object-position:center}
    .field-experience-card figcaption{padding:15px 17px 17px}
    .field-experience-card strong{display:block;margin-bottom:4px;color:var(--navy);font-family:Manrope,sans-serif;font-size:16px}
    .field-experience-card span{display:block;color:var(--muted);font-size:15px;line-height:1.45}
    .field-experience-note{max-width:900px;margin:18px 0 0;color:var(--muted);font-size:13px}
    @media(max-width:900px){.field-experience-grid{grid-template-columns:1fr 1fr}.field-experience-card:last-child{grid-column:1/-1;max-width:520px}}
    @media(max-width:620px){.field-experience-section{padding:58px 0}.field-experience-grid{grid-template-columns:1fr}.field-experience-card:last-child{grid-column:auto;max-width:none}.field-experience-card img{height:215px}}
  `;
  document.head.appendChild(style);

  const section = document.createElement("section");
  section.className = "field-experience-section";
  section.id = "field-experience";
  section.setAttribute("aria-labelledby", "field-experience-title");
  section.innerHTML = `
    <div class="shell">
      <div class="field-experience-intro">
        <p class="eyebrow">Field experience</p>
        <h2 id="field-experience-title">A few examples from prior hands-on work.</h2>
        <p>These are examples from Brian Paul’s earlier water-treatment field work, before Pure Water Pros launched in British Columbia.</p>
      </div>
      <div class="field-experience-grid">
        <figure class="field-experience-card">
          <picture>
            <source media="(max-width:620px)" srcset="/images/gallery/_cache/Quick%20Change%20RO%20System_480.webp" type="image/webp">
            <source srcset="/images/gallery/_cache/Quick%20Change%20RO%20System_800.webp 800w, /images/gallery/_cache/Quick%20Change%20RO%20System_1200.webp 1200w" sizes="(max-width:900px) 50vw, 33vw" type="image/webp">
            <img src="/images/gallery/Quick%20Change%20RO%20System.jpg" alt="Prior field-work example of an under-sink reverse osmosis drinking-water system" loading="lazy" decoding="async">
          </picture>
          <figcaption><strong>Under-sink reverse osmosis</strong><span>Compact drinking-water RO equipment installed inside a kitchen cabinet.</span></figcaption>
        </figure>
        <figure class="field-experience-card">
          <picture>
            <source media="(max-width:620px)" srcset="/images/gallery/_cache/UV%20Dynamics%20Duplex_480.webp" type="image/webp">
            <source srcset="/images/gallery/_cache/UV%20Dynamics%20Duplex_800.webp 800w, /images/gallery/_cache/UV%20Dynamics%20Duplex_1200.webp 1200w" sizes="(max-width:900px) 50vw, 33vw" type="image/webp">
            <img src="/images/gallery/UV%20Dynamics%20Duplex.jpg" alt="Prior field-work example of UV disinfection with dual cartridge filtration" loading="lazy" decoding="async">
          </picture>
          <figcaption><strong>UV + cartridge filtration</strong><span>UV disinfection paired with dual cartridge housings for pretreatment and service access.</span></figcaption>
        </figure>
        <figure class="field-experience-card">
          <picture>
            <source media="(max-width:620px)" srcset="/images/gallery/_cache/New%20Viqua%20VH200-F10%20UV%20System%20with%20Water%20Softener_480.webp" type="image/webp">
            <source srcset="/images/gallery/_cache/New%20Viqua%20VH200-F10%20UV%20System%20with%20Water%20Softener_800.webp 800w, /images/gallery/_cache/New%20Viqua%20VH200-F10%20UV%20System%20with%20Water%20Softener_1200.webp 1200w" sizes="(max-width:900px) 100vw, 33vw" type="image/webp">
            <img src="/images/gallery/New%20Viqua%20VH200-F10%20UV%20System%20with%20Water%20Softener.jpg" alt="Prior field-work example of a residential water softener and UV disinfection system" loading="lazy" decoding="async">
          </picture>
          <figcaption><strong>Softener + UV treatment</strong><span>Residential softener and UV equipment installed together as part of a whole-home treatment setup.</span></figcaption>
        </figure>
      </div>
      <p class="field-experience-note">Shown as prior field experience, not as current Pure Water Pros project photos. Equipment brands shown do not imply dealer affiliation.</p>
    </div>
  `;

  aboutSection.parentNode.insertBefore(section, aboutSection);
})();