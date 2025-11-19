import RiskBadge from "./RiskBadge";

export default function ClauseCard({ clause, onClick }) {
  return (
    <div
      onClick={onClick}
      className="glass-card hover:cursor-pointer hover:scale-[1.02] transition"
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold text-white">{clause.type}</h3>
          <p className="text-gray-300 mt-2">{clause.text}</p>
        </div>

        <RiskBadge risk={clause.risk} />
      </div>
    </div>
  );
}
