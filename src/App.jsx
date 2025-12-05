import { Routes, Route, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";

import LoginPage from "./pages/LoginPage";
import UploadPage from "./pages/UploadPage";
import AnalysisPage from "./pages/AnalysisPage";
import DashboardPage from "./pages/DashboardPage";
import ChatAIPage from "./pages/ChatAIPage";
import ClauseDetailsPage from "./pages/ClauseDetailsPage";
import ComparisonPage from './pages/ComparisonPage';
import NegotiationPage from './pages/NegotiationPage';

export default function App() {
  const location = useLocation();
  const isLoginPage = location.pathname === "/login" || location.pathname === "/";
  const isAuthenticated = sessionStorage.getItem("isAuthenticated") === "true";

  return (
    <div className="min-h-screen flex">
      {!isLoginPage && isAuthenticated && <Sidebar />}

      <div className={`flex-1 ${!isLoginPage && isAuthenticated ? "ml-64" : ""}`}>
        {!isLoginPage && isAuthenticated && <Navbar />}

        <div className={!isLoginPage && isAuthenticated ? "p-8" : ""}>
          <Routes>
            <Route path="/" element={<LoginPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/upload" element={isAuthenticated ? <UploadPage /> : <LoginPage />} />
            <Route path="/analysis" element={isAuthenticated ? <AnalysisPage /> : <LoginPage />} />
            <Route path="/dashboard" element={isAuthenticated ? <DashboardPage /> : <LoginPage />} />
            <Route path="/chat" element={isAuthenticated ? <ChatAIPage /> : <LoginPage />} />
            <Route path="/clause/:id" element={isAuthenticated ? <ClauseDetailsPage /> : <LoginPage />} />
            <Route path="/comparison" element={isAuthenticated ? <ComparisonPage /> : <LoginPage />} />
            <Route path="/negotiation" element={isAuthenticated ? <NegotiationPage /> : <LoginPage />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}
