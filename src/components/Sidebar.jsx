import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const linkStyle = ({ isActive }) =>
    `w-full px-4 py-3 rounded-lg flex items-center gap-3 text-md font-medium transition-all
    ${isActive
      ? "bg-[rgba(114,9,183,0.3)] text-white shadow-lg shadow-[#7209b7]"
      : "text-gray-300 hover:bg-[rgba(255,255,255,0.08)] hover:text-white"
    }`;

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 bg-[rgba(255,255,255,0.05)]
      backdrop-blur-xl border-r border-[rgba(255,255,255,0.15)]
      shadow-[0_0_25px_rgba(114,9,183,0.4)] p-6 flex flex-col">

      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Startup AI</h1>
        <p className="text-sm text-gray-400">Clause Analyzer</p>
      </div>

      <nav className="flex flex-col gap-2">
        <NavLink to="/upload" className={linkStyle}>
          📄 Upload Agreement
        </NavLink>

        <NavLink to="/analysis" className={linkStyle}>
          📊 Analysis Results
        </NavLink>

        <NavLink to="/dashboard" className={linkStyle}>
          📈 Dashboard
        </NavLink>

        <NavLink to="/chat" className={linkStyle}>
          🤖 AI Assistant
        </NavLink>
      </nav>
    </aside>
  );
}
