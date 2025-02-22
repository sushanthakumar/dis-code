import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const DhcpHost = () => {
  const [file, setFile] = useState(null);
  
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

    try {
      const response = await fetch('http://127.0.0.1:5000/v1/dhcpdconf', {
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

  

  return (
    <div className="flex justify-center items-center min-h-screen bg-[#FBE7CC]">
      <div className="bg-orange-100 w-full max-w-md md:max-w-lg lg:max-w-xl xl:max-w-2xl p-6 md:p-8 rounded-2xl shadow-lg transition-all">
        <h2 className="text-2xl md:text-3xl font-semibold text-gray-800 text-center">DHCP Host</h2>
        
        <div className="mb-6">
          <input type="file" onChange={handleFileChange} className="block w-full border p-2 rounded focus:outline focus:outline-black" />
          <button
            onClick={handleUpload}
            className="mt-2 w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-2 px-4 rounded"
          >
            Upload
          </button>
        </div>

        
        <ToastContainer position="top-right" autoClose={5000} />
      </div>
    </div>
  );
};

export default DhcpHost;
