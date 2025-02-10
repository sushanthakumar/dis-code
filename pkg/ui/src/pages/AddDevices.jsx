// AddDevices.js
import React, { useState } from 'react';

const AddDevices = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    if (!selectedFile) {
      alert('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    // Replace with your actual upload URL
    fetch('/device-upload', {
      method: 'POST',
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Upload failed.');
        }
        return response.json();
      })
      .then((data) => {
        alert('File uploaded successfully!');
        // Handle success response
      })
      .catch((error) => {
        alert(`Error: ${error.message}`);
        // Handle error response
      });
  };

  return (
    <div className="h-screen bg-[#FBE7CC] p-6 flex flex-col items-center">
      <h1 className="text-2xl p-2 font-bold">Add Devices</h1>
      <p className="text-sm md:text-base mb-4">
        Upload a file to add devices.
      </p>
      <div className="w-full max-w-md bg-orange-100 p-4 shadow rounded-lg">
        <input
          type="file"
          onChange={handleFileChange}
          className="w-full p-2 border border-gray-300 rounded mb-4"
        />
        <button
          onClick={handleUpload}
          className="bg-orange-400 text-white px-4 py-2 rounded hover:bg-orange-500 transition"
        >
          Upload
        </button>
      </div>
    </div>
  );
};

export default AddDevices;
