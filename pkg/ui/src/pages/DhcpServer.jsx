/*
Project name : SmartConfigNxt
Title : DhcpServer.jsx
Description : Manage the DHCP server by uploading a file containing server configuration.
Author :  Caze Labs
version :1.0 
*/

import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const DhcpServer = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    console.log("Updated status:", status);
  }, [status]);


  useEffect(() => {
    const fetchDhcpStatus = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/v1/dhcpservice/status");

        if (!response.ok) {
          console.error("Failed to fetch DHCP status:", response.status);
          toast.error(`Failed to fetch DHCP status: ${response.status}`);
          return;
        }

        const data = await response.json();

        console.log("Full API Response:", data);

        if (typeof data === "boolean") {
          setStatus(data);
        } else if (data && typeof data.status !== "undefined") {
          setStatus(data.status === true || data.status === "true");
        } else {
          console.error("Invalid API response:", data);
          toast.error("Invalid API response");
        }
      } catch (error) {
        console.error("Error fetching DHCP status:", error);
        toast.error("Error fetching DHCP status");
      }
    };

    fetchDhcpStatus();
  }, []);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.warn("Please select a file to upload.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/v1/dhcpserver", {
        method: "POST",
        headers: {
          "Content-Type": file.type || "application/octet-stream",
          "X-File-Name": file.name,
        },
        body: await file.arrayBuffer(),
      });

      if (response.ok) {
        toast.success("File uploaded successfully.");
      } else {
        toast.error("File upload failed.");
      }
    } catch (error) {
      toast.error("An error occurred during file upload.");
    }
  };

  const handleStart = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/v1/dhcpservice/start", {
        method: "PATCH",
      });

      if (response.ok) {
        setStatus(true);
        toast.success("DHCP started successfully.");
      } else {
        toast.error("Failed to start DHCP.");
      }
    } catch (error) {
      toast.error("An error occurred while starting DHCP.");
    }
  };

  const handleStop = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/v1/dhcpservice/stop", {
        method: "PATCH",
      });

      if (response.ok) {
        setStatus(false);
        toast.success("DHCP stopped successfully.");
      } else {
        toast.error("Failed to stop DHCP.");
      }
    } catch (error) {
      toast.error("An error occurred while stopping DHCP.");
    }
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-[#FBE7CC] p-4">
      <div className="text-center mb-4">
        <h2 className="text-2xl md:text-3xl font-semibold text-gray-800">DHCP Server</h2>
        <p className="text-black text-sm md:text-base">Manage the DHCP server by uploading a file containing server configuration.</p>
      </div>

      <div className="bg-orange-100 w-full max-w-md md:max-w-lg lg:max-w-xl xl:max-w-2xl p-6 md:p-8 rounded-2xl shadow-lg transition-all">
        <div className="mb-6">
          <input type="file" onChange={handleFileChange} className="block w-full border p-2 rounded focus:outline focus:outline-black" />
          <button
            onClick={handleUpload}
            className="mt-2 w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-2 px-4 rounded"
          >
            Upload
          </button>
        </div>

        <div className="text-center">
          {status === null ? (
            <p>Loading...</p>
          ) : status ? (
            <button
              onClick={handleStop}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
            >
              Stop DHCP
            </button>
          ) : (
            <button
              onClick={handleStart}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
            >
              Start DHCP
            </button>
          )}
        </div>

        <ToastContainer position="top-right" autoClose={3000} />
      </div>
    </div>
  );
};

export default DhcpServer;
