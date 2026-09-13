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
