import React from "react";
import FileUpload from "../components/FileUpload";
import { useNavigate } from "react-router-dom";

export default function UploadPage() {
  const navigate = useNavigate();

  const handleDone = (jobId) => {
    sessionStorage.setItem("currentJobId", jobId);
    navigate("/analysis");
  };

  return (
    <div className="glass-card">
      <h1 className="text-2xl font-bold text-white mb-4">Upload Agreement</h1>
      <p className="text-gray-300 mb-5">
        Upload any funding agreement to extract clauses and classify risk.
      </p>

      <FileUpload onUploaded={handleDone} />
    </div>
  );
}
