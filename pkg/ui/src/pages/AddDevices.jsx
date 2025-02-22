import React, { useState } from 'react'; 
import { toast } from "react-toastify"; 

const AddDevices = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    if (!selectedFile) {
      toast.error('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    fetch('http://127.0.0.1:5000/v1/new_upload', {
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
        toast.success('File uploaded successfully!');
      })
      .catch((error) => {
        toast.error(`Error: ${error.message}`);
      });
  };

  
  const handleOkClick = () => {
    fetch('http://127.0.0.1:5000/v1/devices/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({}) 
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to trigger backend function.');
        }
        return response.json();
      })
      .then((data) => {
        toast.success('Devices added  successfully!');
      })
      .catch((error) => {
        toast.error(`Error: ${error.message}`);
      });
  };
  

  return (
    <div className="min-h-screen bg-[#FBE7CC] p-6 flex flex-col items-center">
      <h1 className="text-2xl lg:text-3xl p-2 font-bold">Add Devices</h1>
      <p className="text-sm md:text-base lg:text-lg mb-4 text-center max-w-md">
        Upload a file to add devices.
      </p>

      <div className="w-full max-w-screen-md bg-orange-100 p-6 shadow rounded-lg">
        <input
          type="file"
          onChange={handleFileChange}
          className="w-full p-3 border border-gray-300 rounded mb-4 text-sm md:text-base"
        />
        
       
        <div className="flex flex-wrap justify-center gap-4">
          <button
            onClick={handleUpload}
            className="bg-orange-400 text-white px-5 py-2 rounded hover:bg-orange-500 transition text-sm md:text-base"
          >
            Upload
          </button>
          <button
            onClick={handleOkClick} 
            className="bg-orange-400 text-white px-5 py-2 rounded hover:bg-orange-500 transition text-sm md:text-base"
          >
            OK
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddDevices;
