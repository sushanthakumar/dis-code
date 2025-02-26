/*
Project name : SmartConfigNxt
Title : recommendation.jsx
Description : Provides the recommended deployment use cases based on the devices available.
Author :  Caze Labs
version :1.0 
*/

import React, { useState, useEffect } from "react";
import { useDebouncedCallback } from "use-debounce";

const Recommend = () => {
  const [usecases, setUsecases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedUsecaseId, setSelectedUsecaseId] = useState(null);
  const [details, setDetails] = useState({});


  useEffect(() => {
    const fetchUsecases = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5001/v1/usecases/recommendations");

        if (!response.ok) {

          if (response.status >= 400 && response.status < 500) {
            throw new Error("No recommended use cases");
          }
          throw new Error("No devices found to provide recommendation");
        }

        const data = await response.json();
        setUsecases(data.recommendations);
      } catch (err) {
        setError(err.message || "No recommended use cases");
      } finally {
        setLoading(false);
      }
    };

    fetchUsecases();
  }, []);

  const handleViewMore = useDebouncedCallback(async (usecaseId) => {

    if (selectedUsecaseId === usecaseId) {
      setSelectedUsecaseId(null);
      return;
    }
    if (details[usecaseId]) {
      setSelectedUsecaseId(usecaseId);
      return;
    }

    try {
      setSelectedUsecaseId(usecaseId);
      const response = await fetch(
        `http://127.0.0.1:5001/v1/usecases/${usecaseId}`
      );
      if (!response.ok) {
        throw new Error(
          `Failed to fetch use case details: ${response.statusText}`
        );
      }

      const text = await response.text();
      const sanitizedText = text.replace(/NaN/g, "null");
      const data = JSON.parse(sanitizedText);

      setDetails((prevDetails) => ({
        ...prevDetails,
        [usecaseId]: data.details[0],
      }));
    } catch (error) {
      console.error("Error fetching use case details:", error);
    }
  }, 300);

  return (
    <div className="p-6 bg-[#FBE7CC]  flex-1 flex flex-col min-h-[calc(100vh-100px)] items-center">
      <h1 className="text-2xl p-2 font-bold">Recommended Use cases</h1>
      <p className="text-sm md:text-base mb-4">Provides the recommended deployment use cases based on the devices available</p>


      <div className="w-full max-w-10xl max-h-10xl overflow-hidden">
        <div className="overflow-y-auto max-h-[500px] border border-gray-300 rounded-lg shadow">
          <table className="table-auto w-full text-left border-collapse mb-4">
            <thead className="bg-orange-400 text-white sticky top-0">
              <tr>
                <th className="border px-4 py-2">Usecase ID</th>
                <th className="border px-4 py-2">Description</th>
                <th className="border px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="3" className="text-center py-4">
                    Loading...
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan="3" className="text-center py-4 text-red-500">
                    {error}
                  </td>
                </tr>
              ) : usecases.length > 0 ? (
                usecases.map((usecase, index) => (
                  <React.Fragment key={index}>
                    <tr
                      className={`${index % 2 === 0 ? "bg-orange-100" : "bg-white"
                        }`}
                    >
                      <td className="border px-4 py-2">{usecase.Usecase_ID}</td>
                      <td className="border px-4 py-2">
                        {usecase.Description}
                      </td>
                      <td className="border px-4 py-2 text-center">
                        <button
                          className="text-gray-700 hover:text-orange-500"
                          onClick={() => handleViewMore(usecase.Usecase_ID)}
                        >
                          •••
                        </button>
                      </td>
                    </tr>


                    {selectedUsecaseId === usecase.Usecase_ID && (
                      <tr>
                        <td
                          colSpan="3"
                          className="bg-orange-50 border px-4 py-2"
                        >
                          {details[usecase.Usecase_ID] ? (
                            <table className="table-auto w-full text-left border-collapse">
                              <thead>
                                <tr className="bg-gray-200">
                                  <th className="border px-4 py-2">Key</th>
                                  <th className="border px-4 py-2">Value</th>
                                </tr>
                              </thead>
                              <tbody>
                                {Object.entries(
                                  details[usecase.Usecase_ID]
                                ).map(([key, value]) => (
                                  <tr key={key}>
                                    <td className="border px-4 py-2 font-semibold">
                                      {key}
                                    </td>
                                    <td className="border px-4 py-2">
                                      {value}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          ) : (
                            <p>Loading details...</p>
                          )}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan="3" className="text-center py-4">
                    No use cases found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Recommend;
