(() => {
  const core = document.createElement('script');
  core.src = '/assets/water-problem-checker-core.js?v=2';
  core.defer = true;
  core.addEventListener('load', () => {
    const section = document.getElementById('field-experience');
    const cards = document.querySelectorAll('#field-experience .field-experience-card');
    if (!section || cards.length < 3) return;

    const eyebrow = section.querySelector('.field-experience-intro .eyebrow');
    const heading = section.querySelector('#field-experience-title');
    const intro = section.querySelector('.field-experience-intro > p:not(.eyebrow)');
    const note = section.querySelector('.field-experience-note');
    if (eyebrow) eyebrow.textContent = 'Previous work';
    if (heading) heading.textContent = 'A few pictures from previous water-treatment work.';
    if (intro) intro.textContent = 'Examples of water-treatment systems installed and serviced before Pure Water Pros launched in British Columbia.';
    if (note) note.textContent = 'Examples shown reflect prior field experience. Equipment brands shown do not imply dealer affiliation.';

    const style = document.createElement('style');
    style.textContent = '#field-experience .field-experience-card:first-child img{object-fit:cover!important;padding:0!important;background:#eaf3f6!important}';
    document.head.appendChild(style);

    cards[0].querySelector('picture').innerHTML = '<img src="/assets/field-experience/ro-under-sink.webp" alt="Prior field-work example of a traditional under-sink reverse osmosis system with storage tank" loading="lazy" decoding="async">';
    cards[0].querySelector('figcaption').innerHTML = '<strong>Traditional under-sink reverse osmosis</strong><span>Multi-stage drinking-water RO system and storage tank installed beneath a kitchen sink.</span>';

    cards[1].querySelector('picture').innerHTML = '<img src="/assets/field-experience/uv-prefilter.webp" alt="Prior field-work example of residential UV disinfection with cartridge prefiltration" loading="lazy" decoding="async">';
    cards[1].querySelector('figcaption').innerHTML = '<strong>UV + cartridge prefiltration</strong><span>Residential UV disinfection installed with an upstream cartridge filter on the main water line.</span>';
  });
  document.head.appendChild(core);
})();
// deploy-clean-field-photos