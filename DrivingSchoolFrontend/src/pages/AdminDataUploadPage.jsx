import React, { useState } from "react";
import Header from "../components/Header";
import { toast } from "react-toastify";

const AdminDataUploadPage = () => {
  const [file, setFile] = useState(null);

  const token = localStorage.getItem("access_token");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please, select file");
      return;
    }

    if (file.type !== "application/json") {
      toast.error("Only json files are allowed");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/admins/load_data", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        toast.success(result.detail);
      } else {
        toast.error(result.detail);
      }
    } catch (error) {
      toast.error("Error: " + error.message);
    }
  };

  const handleGenerate = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/admins/generate_data", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });

      const result = await response.json();

      if (response.ok) {
        toast.success(result.detail);
      } else {
        toast.error(result.detail);
      }
    } catch (error) {
      toast.error("Error: " + error.message);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/admins/export_groups", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        toast.error(errorData.detail || "Download failed");
        return;
      }
  
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
  
      const link = document.createElement("a");
      link.href = url;
      link.download = "exported_groups.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
  
      toast.success("File downloaded successfully");
    } catch (error) {
      toast.error("Error: " + error.message);
    }
  };

  return (
    <>
      <Header />
      <div className="flex justify-center bg-gray-50 px-4 h-screen">
        <div className="w-full max-w-4xl mx-auto p-6">
          <h2 className="text-3xl font-bold text-center text-blue-800 mb-4">Data Page</h2>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">

                <input
                    type="file"
                    accept=".json"
                    onChange={handleFileChange}
                    className="block w-full border p-2 rounded-lg"
                />

                <button
                    onClick={handleUpload}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Upload
                </button>

                <div className="flex items-center">
                    <label className="block text-xl font-semibold text-gray-700">Generate test data</label>
                </div>
                <button
                    onClick={handleGenerate}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Generate
                </button>

                <div className="flex items-center">
                    <label className="block text-xl font-semibold text-gray-700">Download group data</label>
                </div>
                <button
                    onClick={handleDownload}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Download
                </button>

            </div>
          </div>

        </div>
      </div>
    </>
  );
};

export default AdminDataUploadPage;
