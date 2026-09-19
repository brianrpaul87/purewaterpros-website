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

  const compactPreview =
    new URLSearchParams(window.location.search).get("preview") === "compact";

  function addHomepageCompressionStyles() {
    const style = document.createElement("style");
    style.textContent = `
      .preview-badge {
        position: fixed;
        right: 16px;
        bottom: 16px;
        z-index: 1000;
        padding: 9px 13px;
        border-radius: 999px;
        background: #08243b;
        color: #fff;
        font: 700 13px/1.2 Manrope, sans-serif;
        box-shadow: 0 10px 26px rgba(8, 36, 59, .24);
      }
      .checker-progress { margin-bottom: 24px; }
      .checker-progress-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 9px;
      }
      .checker-progress-label {
        margin: 0;
        color: var(--navy);
        font-family: Manrope, sans-serif;
        font-size: 14px;
        font-weight: 800;
      }
      .checker-progress-track {
        height: 8px;
        overflow: hidden;
        border-radius: 999px;
        background: #e7eef1;
      }
      .checker-progress-fill {
        display: block;
        height: 100%;
        border-radius: inherit;
        background: linear-gradient(90deg, var(--blue), var(--aqua));
        transition: width .2s ease;
      }
      .checker-navigation {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 8px;
      }
      .checker-back { margin-right: auto; }
      .checker-next, .checker-submit { min-width: 190px; }
      .opening-details {
        margin-top: 26px;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--sand);
      }
      .opening-details summary {
        padding: 16px 18px;
        color: var(--navy);
        font-family: Manrope, sans-serif;
        font-weight: 800;
        cursor: pointer;
      }
      .opening-details-content {
        padding: 0 18px 18px;
        color: var(--muted);
      }
      .opening-details-content p { margin-top: 0; }
      .opening-details-content ul {
        display: grid;
        gap: 9px;
        margin: 14px 0 0;
        padding-left: 20px;
      }
      .checker-section,
      .services-section,
      .process-section,
      .request-section {
        padding-top: 82px;
        padding-bottom: 82px;
      }
      @media (max-width: 680px) {
        .hero,
        .checker-section,
        .services-section,
        .process-section,
        .request-section {
          padding-top: 56px;
          padding-bottom: 56px;
        }
        .checker-navigation {
          display: grid;
          grid-template-columns: 1fr;
        }
        .checker-back {
          order: 2;
          margin-right: 0;
        }
        .checker-back,
        .checker-next,
        .checker-submit {
          width: 100%;
          min-width: 0;
        }
        .service-card { padding: 22px; }
        .service-card > span { margin-bottom: 16px; }
        .process-list li { padding: 16px; }
      }
    `;
    document.head.appendChild(style);

    const badge = document.createElement("div");
    badge.className = "preview-badge";
    badge.textContent = "Compact preview";
    document.body.appendChild(badge);
  }

  function compactOpeningDetails() {
    const launchSection = document.querySelector(".launch-section");
    const launchCard = launchSection?.querySelector(".launch-card");
    const requestIntro = document.querySelector(".request-section .section-intro");
    if (!launchSection || !launchCard || !requestIntro) return;

    const launchCopy = launchCard.querySelector("div > p:last-child");
    const launchList = launchCard.querySelector("ul");
    const details = document.createElement("details");
    details.className = "opening-details";

    const summary = document.createElement("summary");
    summary.textContent = "Opening details";

    const content = document.createElement("div");
    content.className = "opening-details-content";
    if (launchCopy) content.appendChild(launchCopy);
    if (launchList) content.appendChild(launchList);

    details.append(summary, content);
    requestIntro.appendChild(details);

    document.querySelectorAll('a[href="#launch"]').forEach((link) => {
      link.setAttribute("href", "#launch-request");
    });

    launchSection.remove();
  }

  let currentStep = 0;
  let updateStep = () => {};

  if (compactPreview) {
    addHomepageCompressionStyles();
    compactOpeningDetails();

    const fieldsets = Array.from(form.querySelectorAll("fieldset"));
    const submitButton = form.querySelector(".checker-submit");

    const progress = document.createElement("div");
    progress.className = "checker-progress";
    progress.innerHTML = `
      <div class="checker-progress-row">
        <p class="checker-progress-label" aria-live="polite"></p>
      </div>
      <div class="checker-progress-track" aria-hidden="true">
        <span class="checker-progress-fill"></span>
      </div>
    `;

    const navigation = document.createElement("div");
    navigation.className = "checker-navigation";

    const backButton = document.createElement("button");
    backButton.type = "button";
    backButton.className = "button button-secondary checker-back";
    backButton.textContent = "Back";

    const continueButton = document.createElement("button");
    continueButton.type = "button";
    continueButton.className = "button checker-next";
    continueButton.textContent = "Continue";

    form.insertBefore(progress, fieldsets[0]);
    navigation.append(backButton, continueButton);
    form.insertBefore(navigation, submitButton);
    navigation.append(submitButton);

    fieldsets.forEach((fieldset) => {
      fieldset.querySelector("legend")?.setAttribute("tabindex", "-1");
    });

    updateStep = (shouldFocus = true) => {
      fieldsets.forEach((fieldset, index) => {
        fieldset.hidden = index !== currentStep;
      });

      const progressLabel = progress.querySelector(".checker-progress-label");
      const progressFill = progress.querySelector(".checker-progress-fill");
      progressLabel.textContent = `Question ${currentStep + 1} of ${fieldsets.length}`;
      progressFill.style.width = `${((currentStep + 1) / fieldsets.length) * 100}%`;

      backButton.hidden = currentStep === 0;
      continueButton.hidden = currentStep === fieldsets.length - 1;
      submitButton.hidden = currentStep !== fieldsets.length - 1;
      error.hidden = true;

      if (shouldFocus) {
        fieldsets[currentStep].querySelector("legend")?.focus();
      }
    };

    function currentStepAnswered() {
      return Boolean(fieldsets[currentStep]?.querySelector("input:checked"));
    }

    continueButton.addEventListener("click", () => {
      if (!currentStepAnswered()) {
        error.textContent = "Choose an answer to continue.";
        error.hidden = false;
        fieldsets[currentStep].querySelector("input")?.focus();
        return;
      }

      currentStep += 1;
      updateStep();
    });

    backButton.addEventListener("click", () => {
      if (currentStep === 0) return;
      currentStep -= 1;
      updateStep();
    });

    form.addEventListener("change", (event) => {
      if (event.target.matches('input[type="radio"]')) error.hidden = true;
    });

    updateStep(false);
  }

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
      error.textContent = "Please answer all four questions.";
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

    if (compactPreview) {
      currentStep = 0;
      updateStep(false);
    }

    form.querySelector("input")?.focus();
  });
})();