const json = browser.runtime.getURL("cities_data.json");
console.log(json);

function getCities() {
  const elements = document.querySelectorAll("#play-zone .boussole a");
  return Array.from(elements);
}

function cheat(data) {
  const cities = getCities();
  for (const city of cities) {
    const distance = data[city.innerText];
    if(distance === undefined) continue;
    city.innerText += ` (${distance})`;
  }
}

fetch(json).then(response => response.json()).then(json => cheat(json));
