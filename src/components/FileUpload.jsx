import React, { useState } from "react";
import { uploadAgreement } from "../utils/api";

export default function FileUpload({ onUploaded, metadata }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return alert("Select a file first!");

    setLoading(true);
    const res = await uploadAgreement(file, metadata);
    setLoading(false);

    if (res.success) {
      onUploaded(res.jobId);
    }
  };

  return (
    <div className="glass-card glow">
      <h2 className="text-xl font-semibold text-white mb-4">Upload Agreement</h2>

      <input
        type="file"
        accept=".pdf,.doc,.docx"
        onChange={(e) => setFile(e.target.files[0])}
        className="w-full text-gray-300 mb-4"
      />

      <button onClick={handleUpload} className="neon-btn">
        {loading ? "Uploading..." : "Upload & Analyze"}
      </button>
    </div>
  );
}
