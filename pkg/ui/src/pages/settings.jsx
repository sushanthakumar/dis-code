import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { addTag, deleteTag, setTags } from "../store/store";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


const transformTags = (data) => {
  return data.map((item) => {
    const tagObject = item[1] || {};
    const key = Object.keys(tagObject).find((key) => key.trim()) || "";
    const value = tagObject[key] || "";
    return {
      id: item[0]?.Id,
      key,
      value,
    };
  });
};

const Settings = () => {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");

  const tags = useSelector((state) => state.tags);
  const dispatch = useDispatch();

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/v1/customtags");
        if (!response.ok) {
          throw new Error("Failed to fetch tags.");
        }
        const data = await response.json();
        const transformedTags = transformTags(data);
        dispatch(setTags(transformedTags));
      } catch (error) {
        toast.error(`Error fetching tags: ${error.message}`);
      }
    };

    fetchTags();
  }, [dispatch]);

  const handleAddTag = async () => {
    if (key.trim() && value.trim()) {
      try {
        const payload = {
          Tags: {
            [key]: value,
          },
        };

        const response = await fetch("http://127.0.0.1:5000/v1/customtags", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error("Failed to add tag.");
        }

        const data = await response.json();
        dispatch(addTag({ id: data.id, key, value }));
        setKey("");
        setValue("");
        toast.success("Tag added successfully!");
      } catch (error) {
        toast.error(`Error adding tag: ${error.message}`);
      }
    } else {
      toast.warn("Please provide both key and value.");
    }
  };

  const handleDeleteTag = async (id) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/v1/customtags?id=${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete tag.");
      }

      dispatch(deleteTag(id));
      toast.success("Tag deleted successfully!");
    } catch (error) {
      toast.error(`Error deleting tag: ${error.message}`);
    }
  };

  return (
    <div className="h-screen bg-[#FBE7CC] p-6 flex flex-col items-center">
      <h1 className="text-2xl p-2 font-bold">Tags</h1>
      <p className="text-sm md:text-base mb-4 text-center max-w-md">
        Create custom groups through tags. This will be used to group devices.
      </p>

      <div className="bg-orange-100 w-full max-w-md md:max-w-lg lg:max-w-xl xl:max-w-2xl p-4 md:p-6 rounded-2xl shadow-lg transition-all mb-2">
        <h2 className="text-2xl md:text-3xl font-semibold text-gray-800 text-center">
          Create a new tag
        </h2>
        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2" htmlFor="key">
            Key
          </label>
          <input
            id="key"
            type="text"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-400"
            placeholder="Enter tag key"
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 font-medium mb-2" htmlFor="value">
            Value
          </label>
          <input
            id="value"
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-400"
            placeholder="Enter tag value"
          />
        </div>
        <button
          onClick={handleAddTag}
          className="bg-orange-400 text-white px-4 py-2 rounded hover:bg-orange-500 transition"
        >
          Add Tag
        </button>
      </div>

      <div className="bg-orange-100 w-full max-w-md md:max-w-lg lg:max-w-xl xl:max-w-2xl p-4 md:p-6 overflow-auto rounded-2xl shadow-lg transition-all">
        <h2 className="text-2xl md:text-2xl font-semibold text-gray-800 text-center pb-2">
          List of Available Tags
        </h2>
        {tags.length === 0 ? (
          <p className="bg-white p-2 rounded text-gray-700 text-center">No tags created yet.</p>
        ) : (
          <ul className="space-y-4">
            {tags.map((tag) => (
              <li
                key={tag.id}
                className="flex justify-between items-center bg-white p-3 rounded"
              >
                <div>
                  <span className="font-bold text-gray-700">Key:</span> {tag.key},{" "}
                  <span className="font-bold text-gray-700">Value:</span> {tag.value}
                </div>
                <button
                  onClick={() => handleDeleteTag(tag.id)}
                  className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 transition"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <ToastContainer position="top-right" autoClose={5000} />
    </div>
  );
};

export default Settings;
