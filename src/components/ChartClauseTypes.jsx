import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function ChartClauseTypes({ data }) {
  const labels = Object.keys(data);
  const values = Object.values(data);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Count",
        data: values,
        backgroundColor: "#7209b7",
        borderColor: "#4cc9f0",
        borderWidth: 2
      }
    ]
  };

  return (
    <div className="glass-card">
      <h3 className="text-xl font-bold text-white mb-3">
        Clause Type Distribution
      </h3>
      <Bar data={chartData} />
    </div>
  );
}
