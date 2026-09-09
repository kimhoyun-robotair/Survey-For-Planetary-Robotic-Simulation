"use strict";

const filters = document.querySelector("#filters");
const records = [...document.querySelectorAll(".record")];
const search = document.querySelector("#search");
const domain = document.querySelector("#domain");
const platform = document.querySelector("#platform");
const access = document.querySelector("#access");
const count = document.querySelector("#record-count");
const empty = document.querySelector("#empty-state");

function filterRecords() {
  const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const record of records) {
    const matches = terms.every(term => record.dataset.search.includes(term))
      && (!domain.value || record.dataset.domain === domain.value)
      && (!platform.value || record.dataset.platform === platform.value)
      && (!access.value || record.dataset.access === access.value);
    record.hidden = !matches;
    if (matches) visible += 1;
  }
  count.textContent = `${visible} of ${records.length} works`;
  empty.hidden = visible !== 0;
}

filters.hidden = false;
filters.addEventListener("input", filterRecords);
filters.addEventListener("change", filterRecords);
filters.addEventListener("submit", event => event.preventDefault());
filters.addEventListener("reset", () => requestAnimationFrame(filterRecords));
