// GitHub Pages cannot run the original GoDaddy API. Set a CORS-enabled backend here.
window.FEuchteCheckConfig = {
  apiBase: "https://feuchtecheck.at",
  // Fallback when the API is unreachable: simplified, indicative estimate computed in the browser.
  // This is NOT the original server logic; amounts differ from feuchtecheck.at.
  estimate: function (a) {
    var s = a.symptom, t = a.timing, y = a.buildingYear, sz = a.problemSize;
    var cause = "Feuchtigkeit im Mauerwerk", low = 1800, high = 4500, priority = "normal";
    var checks = ["Feuchtemessung vor Ort empfohlen", "Übergang zwischen Boden und Wand prüfen", "Sanierungsart erst nach Ursachenklärung festlegen"];
    if (t === "nach-regen" || s === "wasser-am-boden") {
      cause = "seitlich eindringende Feuchtigkeit / Abdichtungsproblem"; low = 3500; high = 8500;
      checks = ["Außenabdichtung bzw. Wandanschlüsse prüfen", "Drainage und Geländegefälle kontrollieren", "Bei akutem Wassereintritt zeitnah besichtigen lassen"];
    } else if (s === "salzausbluehungen" || (y === "vor-1945" && s === "feuchte-wand")) {
      cause = "aufsteigende Feuchtigkeit möglich"; low = 2500; high = 6500;
      checks = ["Horizontalsperre bzw. Injektionsverfahren prüfen", "Salzbelastung des Mauerwerks beurteilen", "Putzaufbau nach Trocknung sanieren"];
    } else if (t === "nur-sommer" || s === "muffiger-geruch") {
      cause = "Kondensation / hohe Luftfeuchte möglich"; low = 500; high = 3000;
      checks = ["Raumluftfeuchte messen", "Lüftungsverhalten und kalte Oberflächen prüfen", "Bauliche Durchfeuchtung ausschließen"];
    } else if (s === "schimmel" && t === "im-winter") {
      cause = "Kondensation oder Wärmebrücke möglich"; low = 700; high = 3500;
      checks = ["Oberflächentemperatur und Luftfeuchte messen", "Wärmebrücken prüfen", "Schimmelursache vor Sanierung klären"];
    }
    if (sz === "mehrere-waende") { low *= 1.25; high *= 1.35; }
    if (sz === "ganzer-keller") { low *= 1.7; high *= 1.9; }
    if (sz === "kleine-stelle") { low *= 0.7; high *= 0.7; }
    if (s === "wasser-am-boden" || t === "ploetzlich" || sz === "ganzer-keller") priority = "high";
    return { result: {
      diagnosis: "Mögliche Ursache: " + cause,
      costMin: Math.round(low / 100) * 100,
      costMax: Math.round(high / 100) * 100,
      checks: checks, priority: priority
    }, leadId: "offline" };
  }
};
