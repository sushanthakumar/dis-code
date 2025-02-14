import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const DhcpServer = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('stopped'); 

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.warn('Please select a file to upload.');
      return;
    }
  
    const formData = new FormData();
    formData.append('file', file);
  
    // Log the FormData contents
    console.log("Uploading File Details:");
    for (const [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`Key: ${key}, Name: ${value.name}, Size: ${value.size} bytes, Type: ${value.type}`);
      } else {
        console.log(`Key: ${key}, Value: ${value}`);
      }
    }
  
    try {
      const response = await fetch('/dhcp-server-upload', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        toast.success('File uploaded successfully.');
      } else {
        alert('File upload failed.');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error('An error occurred during file upload.');
    }
  };
  
  const handleStart = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/v1/dhcpservice/start', {
        method: 'PATCH',
      });

      if (response.ok) {
        setStatus('started');
        toast.success('DHCP started successfully.');
      } else {
        toast.error('Failed to start DHCP.');
      }
    } catch (error) {
      console.error('Error starting DHCP:', error);
      toast.error('An error occurred while starting DHCP.');
    }
  };

  const handleStop = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/v1/dhcpservice/stop', {
        method: 'PATCH',
      });

      if (response.ok) {
        setStatus('stopped');
        toast.success('DHCP stopped successfully.');
      } else {
        toast.error('Failed to stop DHCP.');
      }
    } catch (error) {
      console.error('Error stopping DHCP:', error);
      toast.error('An error occurred while stopping DHCP.');
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-[#FBE7CC]">
      <div className="bg-orange-100 shadow-lg rounded-lg p-6 w-full max-w-lg">
        <h2 className="text-2xl font-bold mb-4 text-center">DHCP Server</h2>
        
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
          {status === "stopped" ? (
            <button
              onClick={handleStart}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
            >
              Start DHCP
            </button>
          ) : (
            <button
              onClick={handleStop}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
            >
              Stop DHCP
            </button>
          )}
        </div>

        <ToastContainer position="top-right" autoClose={5000} />
      </div>
    </div>
  );
};

export default DhcpServer;
