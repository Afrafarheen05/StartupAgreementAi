export default function RiskBadge({ risk }) {
  const colors = {
    High: "bg-red-500",
    Medium: "bg-yellow-400 text-black",
    Low: "bg-green-400 text-black",
  };

  return (
    <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${colors[risk]}`}>
      {risk}
    </span>
  );
}
