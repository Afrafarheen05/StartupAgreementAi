import React from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function ChartRiskPie({ data }) {
  const chartData = {
    labels: ["High", "Medium", "Low"],
    datasets: [
      {
        data: [data.high, data.medium, data.low],
        backgroundColor: ["#f72585", "#ffd166", "#4ee44e"],
        borderColor: "#120026",
        borderWidth: 3,
      }
    ]
  };

  return (
    <div className="glass-card">
      <h3 className="text-xl font-bold text-white mb-3">Risk Breakdown</h3>
      <Pie data={chartData} />
    </div>
  );
}
