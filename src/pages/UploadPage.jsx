import React, { useState } from "react";
import FileUpload from "../components/FileUpload";
import StartupTypeSelector from "../components/StartupTypeSelector";
import { useNavigate } from "react-router-dom";

export default function UploadPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1 = Type Selection, 2 = File Upload
  const [startupMetadata, setStartupMetadata] = useState(null);

  const handleTypeSelected = (metadata) => {
    setStartupMetadata(metadata);
    setStep(2);
  };

  const handleDone = (jobId) => {
    sessionStorage.setItem("currentJobId", jobId);
    sessionStorage.setItem("startupMetadata", JSON.stringify(startupMetadata));
    navigate("/analysis");
  };

  return (
    <div>
      {step === 1 ? (
        <StartupTypeSelector onComplete={handleTypeSelected} />
      ) : (
        <div className="glass-card">
          <div className="mb-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-400">Selected: </span>
                <span className="text-white font-semibold">
                  {startupMetadata.type} • {startupMetadata.stage}
                </span>
              </div>
              <button
                onClick={() => setStep(1)}
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Change
              </button>
            </div>
          </div>

          <h1 className="text-2xl font-bold text-white mb-4">Upload Agreement</h1>
          <p className="text-gray-300 mb-5">
            Upload your funding agreement, term sheet, or investment contract for AI-powered risk analysis.
          </p>

          <FileUpload onUploaded={handleDone} metadata={startupMetadata} />
        </div>
      )}
    </div>
  );
}
