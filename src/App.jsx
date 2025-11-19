import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";

import UploadPage from "./pages/UploadPage";
import AnalysisPage from "./pages/AnalysisPage";
import DashboardPage from "./pages/DashboardPage";
import ChatAIPage from "./pages/ChatAIPage";
import ClauseDetailsPage from "./pages/ClauseDetailsPage";

export default function App() {
  return (
    <div className="min-h-screen flex">

      <Sidebar />

      <div className="flex-1 ml-64">
        <Navbar />

        <div className="p-8">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/chat" element={<ChatAIPage />} />
            <Route path="/clause/:id" element={<ClauseDetailsPage />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}
