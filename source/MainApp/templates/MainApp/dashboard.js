function loadTransactionsChart() {
  fetch("/finances/api/stats-finance/") // ton endpoint Django
    .then(response => response.json())
    .then(data => {
      // Extraire les valeurs pour le graphique
      const labels = data.map(item => item.mois);
      const depots = data.map(item => item.depots);
      const retraits = data.map(item => item.retraits);
      const remboursements = data.map(item => item.remboursements);
      const depot_fidelis = data.map(item => item.depot_fidelis);
      const retrait_fidelis = data.map(item => item.retrait_fidelis);

      // Construire le chart
      new CustomEChart({
        selector: "#orders-chart",
        options: () => ({
          tooltip: {
            trigger: "axis",
            padding: [8, 15],
            backgroundColor: ins("secondary-bg"),
            borderColor: ins("border-color"),
            textStyle: { color: ins("light-text-emphasis") },
            borderWidth: 1,
            transitionDuration: .125,
            axisPointer: { type: "none" }
          },
          legend: {
            data: ["Dépôts Fidelis", "Retraits Fidelis", "Remboursements", "Dépôts épargnes", "Retraits épargnes", ],
            top: 15,
            textStyle: { color: ins("body-color") }
          },
          xAxis: {
            data: labels,
            axisLine: { lineStyle: { type: "dashed", color: ins("border-color") } },
            axisLabel: { color: ins("secondary-color") }
          },
          yAxis: {
            axisLine: { lineStyle: { type: "dashed", color: ins("border-color") } },
            axisLabel: { color: ins("secondary-color") },
            splitLine: { show: false }
          },
          grid: { left: 25, right: 25, bottom: 25, top: 60, containLabel: true },
          series: [
            {
              name: "Dépôts Fidelis",
              type: "line",
              barWidth: 14,
              itemStyle: { borderRadius: [5, 5, 0, 0], color: ins("success") },
              data: depot_fidelis
            },
            {
              name: "Retraits Fidelis",
              type: "line",
              barWidth: 14,
              itemStyle: { borderRadius: [5, 5, 0, 0], color: ins("warning") },
              data: retrait_fidelis,  
            },
            {
              name: "Remboursements",
              type: "line",
              barWidth: 14,
              itemStyle: { borderRadius: [5, 5, 0, 0], color: ins("primary") },
              data: remboursements
            },
            {
              name: "Dépôts épargnes",
              type: "bar",
              barWidth: 14,
              itemStyle: { borderRadius: [5, 5, 0, 0], color: ins("purple") },
              data: depots
            },
            {
              name: "Retraits épargnes",
              type: "bar",
              barWidth: 14,
              itemStyle: { borderRadius: [5, 5, 0, 0], color: ins("danger") },
              data: retraits
            },
          ]
        })
      });
    })
    .catch(error => {
      console.error("Erreur lors du chargement des stats transactions:", error);
    });
}

// Charger le graph après le DOM
document.addEventListener("DOMContentLoaded", loadTransactionsChart);
