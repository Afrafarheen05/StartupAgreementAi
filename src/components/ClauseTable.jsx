import ClauseCard from "./ClauseCard";

export default function ClauseTable({ clauses, onSelect }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {clauses.map((c) => (
        <ClauseCard key={c.id} clause={c} onClick={() => onSelect(c)} />
      ))}
    </div>
  );
}
