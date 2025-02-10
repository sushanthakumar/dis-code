import React, { useEffect, useState } from "react";

const UseCases = () => {
  const [useCases, setUseCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); 

  useEffect(() => {
    const fetchUseCases = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5001/v1/usecases/");
        const text = await response.text();

       
        const sanitizedText = text.replace(/\bNaN\b/g, "null");
        const data = JSON.parse(sanitizedText);

        setUseCases(data);
      } catch (err) {
        console.error("Error fetching use cases:", err);
        setError("Failed to fetch use cases."); 
      } finally {
        setLoading(false);
      }
    };

    fetchUseCases();
  }, []);

  return (
    <div className="p-6 bg-[#FBE7CC] flex-1 flex flex-col min-h-[calc(100vh-100px)] items-center">
      <h2 className="text-2xl font-bold mb-4">Use Cases</h2>
      <p className="text-sm md:text-base mb-4">
        Provides the supported use cases for deployment
      </p>

      <div className="w-full max-w-7xl overflow-hidden">
        <div className="overflow-y-auto max-h-[500px] border border-gray-300 rounded-lg shadow">
          <table className="table-auto w-full text-left border-collapse">
            <thead className="bg-orange-400 text-white sticky top-0">
              <tr>
                <th className="border px-4 py-2">ID</th>
                <th className="border px-4 py-2">Description</th>
                <th className="border px-4 py-2">Server Type</th>
                <th className="border px-4 py-2">Server Count</th>
                <th className="border px-4 py-2">Switch Type</th>
                <th className="border px-4 py-2">Switch Count</th>
                <th className="border px-4 py-2">Storage Type</th>
                <th className="border px-4 py-2">Storage Count</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-4">
                    Loading...
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan="8" className="text-center py-4 text-red-500">
                    {error}
                  </td>
                </tr>
              ) : useCases.length > 0 ? (
                useCases.map((useCase, index) => (
                  <tr
                    key={useCase.ID}
                    className={`${
                      index % 2 === 0 ? "bg-orange-100" : "bg-white"
                    }`}
                  >
                    <td className="border px-4 py-2">{useCase.ID}</td>
                    <td className="border px-4 py-2">
                      {useCase.Description || "-"}
                    </td>
                    <td className="border px-4 py-2">
                      {useCase.Server_Type || "-"}
                    </td>
                    <td className="border px-4 py-2">
                      {useCase.Server_Count || "-"}
                    </td>
                    <td className="border px-4 py-2">
                      {useCase.Switch_Type || "-"}
                    </td>
                    <td className="border px-4 py-2">
                      {useCase.Switch_Count || "-"}
                    </td>
                    <td className="border px-4 py-2">
                      {useCase.Storage_Type || "-"}
                    </td>
                    <td className="border px-4 py-2">
                      {useCase.Storage_Count || "-"}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="text-center py-4">
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

export default UseCases;
