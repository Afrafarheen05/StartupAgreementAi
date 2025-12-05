import { NavLink } from "react-router-dom";
import { Upload, BarChart3, LayoutDashboard, MessageSquare, Scale, Target, Shield, TrendingUp, FileText } from "lucide-react";

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
      shadow-[0_0_25px_rgba(114,9,183,0.4)] p-6 flex flex-col overflow-y-auto">

      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">AgreeShield AI</h1>
        <p className="text-sm text-gray-400">Legal Tech Platform</p>
      </div>

      <nav className="flex flex-col gap-2">
        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-4 mb-2 px-4">
          Core Features
        </div>
        
        <NavLink to="/upload" className={linkStyle}>
          <Upload className="w-4 h-4" />
          Upload Agreement
        </NavLink>

        <NavLink to="/analysis" className={linkStyle}>
          <BarChart3 className="w-4 h-4" />
          Analysis Results
        </NavLink>

        <NavLink to="/dashboard" className={linkStyle}>
          <LayoutDashboard className="w-4 h-4" />
          Dashboard
        </NavLink>

        <NavLink to="/chat" className={linkStyle}>
          <MessageSquare className="w-4 h-4" />
          AI Assistant
        </NavLink>

        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mt-6 mb-2 px-4">
          Advanced Tools
        </div>

        <NavLink to="/comparison" className={linkStyle}>
          <Scale className="w-4 h-4" />
          Compare Deals
        </NavLink>

        <NavLink to="/negotiation" className={linkStyle}>
          <Target className="w-4 h-4" />
          Negotiation Simulator
        </NavLink>
      </nav>

      <div className="mt-auto pt-6 border-t border-gray-700">
        <div className="text-xs text-gray-400 text-center">
          <div className="font-semibold text-white mb-1">✨ All Features Active</div>
          <div>Enterprise Legal-Tech Platform</div>
        </div>
      </div>
    </aside>
  );
}
