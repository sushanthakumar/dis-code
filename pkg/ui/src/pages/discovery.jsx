import React, { useReducer, useEffect, useMemo, useCallback } from "react";
import { FaSyncAlt, FaSearch, FaSpinner, FaCheckCircle, FaFilter } from "react-icons/fa";
import { useSelector, useDispatch as useReduxDispatch } from "react-redux";
import { setTags } from "../store/store";

// --- Local State Management using useReducer ---

const initialState = {
  devices: [],
  loading: true,
  error: null,
  selectedRows: new Set(),
  selectAll: false,
  tagsVisible: false,
  searchInput: "",
  searchVisible: false,
  itemsPerPage: 10,
  currentPage: 1,
  activeTab: "discovered",
  groupTab: "switches",
  tagsLoading: true,
  selectedTag: null,
  selectedDeviceId: null,
  healthStatus: {},
  tagsDropdownVisible: false,
  selectedTags: new Set(),
  notification: "",
  isTagFilterVisible: false, 
  activeTagFilter: null,
};



function reducer(state, action) {
  switch (action.type) {
    case "SET_DEVICES":
      return { ...state, devices: action.payload };
    case "SET_LOADING":
      return { ...state, loading: action.payload };
    case "SET_ERROR":
      return { ...state, error: action.payload };
    case "SET_SELECTED_ROWS":
      return { ...state, selectedRows: action.payload };
    case "TOGGLE_SELECT_ALL":
      return {
        ...state,
        selectAll: !state.selectAll,
        selectedRows: action.payload,
      };
    case "SET_SEARCH_INPUT":
      return { ...state, searchInput: action.payload };
    case "SET_SEARCH_VISIBLE":
      return { ...state, searchVisible: action.payload };
    case "SET_CURRENT_PAGE":
      return { ...state, currentPage: action.payload };
    case "SET_ACTIVE_TAB":
      return { ...state, activeTab: action.payload };
    case "SET_GROUP_TAB":
      return { ...state, groupTab: action.payload };
    case "SET_TAGS_LOADING":
      return { ...state, tagsLoading: action.payload };
    case "SET_SELECTED_TAG":
      return { ...state, selectedTag: action.payload };
    case "SET_SELECTED_DEVICE_ID":
      return { ...state, selectedDeviceId: action.payload };
    case "UPDATE_DEVICE_TAG":
      return {
        ...state,
        devices: state.devices.map((device) =>
          device["ID"] === action.payload.deviceId
            ? { ...device, Tag: action.payload.tagKeyValue }
            : device
        ),
      };
    case "SET_HEALTH_STATUS":
      return {
        ...state,
        healthStatus: { ...state.healthStatus, ...action.payload },
      };
    case "SET_TAGS_DROPDOWN_VISIBLE":
      return { ...state, tagsDropdownVisible: action.payload };
    case "SET_SELECTED_TAGS":
      return { ...state, selectedTags: action.payload };
    case "SET_ITEMS_PER_PAGE":
      return { ...state, itemsPerPage: action.payload };
    case "SET_NOTIFICATION":
      return { ...state, notification: action.payload };
    case "TOGGLE_TAG_FILTER_VISIBILITY":
      return { ...state, isTagFilterVisible: !state.isTagFilterVisible };
    case "SET_ACTIVE_TAG_FILTER":
      return { ...state, activeTagFilter: action.payload };
    default:
      return state;
  }
}

// --- Discovery Component ---
const Discovery = () => {
  const [state, localDispatch] = useReducer(reducer, initialState);
  const reduxDispatch = useReduxDispatch();
  const tags = useSelector((state) => state.tags);

  // Missing function implementations:
  const toggleSearchVisibility = useCallback(() => {
    localDispatch({
      type: "SET_SEARCH_VISIBLE",
      payload: !state.searchVisible,
    });
  }, [state.searchVisible]);

  const handleSearchInputChange = useCallback((e) => {
    localDispatch({ type: "SET_SEARCH_INPUT", payload: e.target.value });
  }, []);

  const handleReload = useCallback(() => {
    window.location.reload();
  }, []);

  const setActiveTabToDiscovered = useCallback(() => {
    localDispatch({ type: "SET_ACTIVE_TAB", payload: "discovered" });
  }, []);

  const setActiveTabToGrouping = useCallback(() => {
    localDispatch({ type: "SET_ACTIVE_TAB", payload: "grouping" });
  }, []);

  const setGroupTabToSwitches = useCallback(() => {
    localDispatch({ type: "SET_GROUP_TAB", payload: "switches" });
  }, []);

  const setGroupTabToFabric = useCallback(() => {
    localDispatch({ type: "SET_GROUP_TAB", payload: "fabricInterconnect" });
  }, []);

  const setGroupTabToStorages = useCallback(() => {
    localDispatch({ type: "SET_GROUP_TAB", payload: "storages" });
  }, []);

  // Optimized fetchTags with try/catch and array transformation
  const fetchTags = useCallback(async () => {
    localDispatch({ type: "SET_TAGS_LOADING", payload: true });
    try {
      const response = await fetch("http://127.0.0.1:5000/v1/customtags");
      if (!response.ok) throw new Error("Failed to fetch tags");
      const data = await response.json();

      const transformedTags = data
        .map((item) => {
          const id = item.Id;
          const keyValuePairs = Object.entries(item).filter(
            ([key, value]) => key !== "Id" && key.trim() && value.trim()
          );
          return keyValuePairs.map(([key, value]) => ({
            id,
            key,
            value,
          }));
        })
        .flat();

      reduxDispatch(setTags(transformedTags));
    } catch (err) {
      console.error("Error fetching tags:", err.message);
    } finally {
      localDispatch({ type: "SET_TAGS_LOADING", payload: false });
    }
  }, [reduxDispatch]);

  useEffect(() => {
    fetchTags(); 
  }, [fetchTags]);
  
  
  
  useEffect(() => {
    const fetchData = async () => {
      localDispatch({ type: "SET_LOADING", payload: true });
      try {
        await Promise.all([
          fetchTags(),
          (async () => {
            const scanResponse = await fetch("http://127.0.0.1:5000/v1/synclist");
            if (!scanResponse.ok)
              throw new Error(`Scan Error: ${scanResponse.statusText}`);
            await scanResponse.json();
          })(),
        ]);

        const listResponse = await fetch("http://127.0.0.1:5000/v1/devices");
        if (!listResponse.ok)
          throw new Error(`List Error: ${listResponse.statusText}`);
        const listData = await listResponse.json();
        
      console.log("Raw List API Response:", listData);
      console.log("Total Items Received:", listData.length);

        localDispatch({ type: "SET_DEVICES", payload: listData });
      } catch (err) {
        localDispatch({ type: "SET_ERROR", payload: err.message });
      } finally {
        localDispatch({ type: "SET_LOADING", payload: false });
      }
    };

    fetchData();
  }, [fetchTags]);

  
  const handleTagAssign = useCallback(async (deviceId, tagKeyValue) => {
    try {
      console.log("Assigning tag:", { deviceId, tagKeyValue });

      const response = await fetch(
        `http://127.0.0.1:5000/v1/devices/${deviceId}/tags`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            accept: "application/json",
          },
          body: JSON.stringify({ Tag: tagKeyValue }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to assign tag: ${response.statusText}`);
      }

      localDispatch({
        type: "UPDATE_DEVICE_TAG",
        payload: { deviceId, tagKeyValue },
      });
      localDispatch({
        type: "SET_NOTIFICATION",
        payload: "Tag assigned successfully!",
      });
      setTimeout(() => {
        localDispatch({ type: "SET_NOTIFICATION", payload: "" });
      }, 3000);
      console.log("Tag assigned successfully!");
    } catch (error) {
      console.error("Error assigning tag:", error);
      localDispatch({
        type: "SET_NOTIFICATION",
        payload: "Failed to assign tag.",
      });
      setTimeout(() => {
        localDispatch({ type: "SET_NOTIFICATION", payload: "" });
      }, 3000);
      console.log("Failed to assign tag.");
    }
  }, []);

  const handleSelectAllChange = useCallback(() => {
    if (state.selectAll) {
      localDispatch({ type: "SET_SELECTED_ROWS", payload: new Set() });
    } else {
      const allIndexes = new Set(
        state.devices
          .slice(
            (state.currentPage - 1) * state.itemsPerPage,
            state.currentPage * state.itemsPerPage
          )
          .map((_, idx) => idx)
      );
      localDispatch({ type: "SET_SELECTED_ROWS", payload: allIndexes });
    }
    localDispatch({ type: "TOGGLE_SELECT_ALL", payload: state.selectedRows });
  }, [
    state.devices,
    state.currentPage,
    state.itemsPerPage,
    state.selectAll,
    state.selectedRows,
  ]);

  const handleRowCheckboxChange = useCallback(
    (deviceId) => {
      localDispatch({
        type: "SET_SELECTED_DEVICE_ID",
        payload: state.selectedDeviceId === deviceId ? null : deviceId,
      });
    },
    [state.selectedDeviceId]
  );

  const handleHealthCheck = useCallback(async () => {
    if (!state.selectedDeviceId) return;
    try {
      localDispatch({
        type: "SET_HEALTH_STATUS",
        payload: { [state.selectedDeviceId]: "Checking..." },
      });

      const response = await fetch(
        `http://127.0.0.1:5000/v1/devices/healthcheck/${state.selectedDeviceId}`,
        {
          method: "PATCH",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        }
      );

      if (!response.ok) throw new Error("Health check failed");

      const result = await response.json();
      localDispatch({
        type: "SET_HEALTH_STATUS",
        payload: {
          [state.selectedDeviceId]: result.updated_record?.status || "Unknown",
        },
      });
    } catch (err) {
      console.error("Error in health check:", err);
      localDispatch({
        type: "SET_HEALTH_STATUS",
        payload: { [state.selectedDeviceId]: "Error" },
      });
    }
  }, [state.selectedDeviceId]);

  const handleItemsPerPageChange = useCallback((value) => {
    localDispatch({ type: "SET_ITEMS_PER_PAGE", payload: value });
    localDispatch({ type: "SET_CURRENT_PAGE", payload: 1 });
  }, []);

  const totalPages = useMemo(
    () => Math.ceil(state.devices.length / state.itemsPerPage),
    [state.devices, state.itemsPerPage]
  );

  const handlePreviousPage = useCallback(() => {
    localDispatch({
      type: "SET_CURRENT_PAGE",
      payload:
        state.currentPage > 1 ? state.currentPage - 1 : state.currentPage,
    });
  }, [state.currentPage]);

  const handleNextPage = useCallback(() => {
    localDispatch({
      type: "SET_CURRENT_PAGE",
      payload:
        state.currentPage < totalPages
          ? state.currentPage + 1
          : state.currentPage,
    });
  }, [state.currentPage, totalPages]);

  const getFilteredDevices = useMemo(() => {
    let devicesToFilter = state.devices;
    console.log("Before Inventory Type Filter:", devicesToFilter.length);

    if (state.activeTab === "discovered") {
      console.log("Discovered Devices Tab Active: Returning All Devices");
      return devicesToFilter;
  }
    if (state.groupTab === "switches") {
      devicesToFilter = devicesToFilter.filter(
        (device) =>
          device["Inventory_Type"] === "MDS" ||
          device["Inventory_Type"] === "Nexus 9K"
      );
      console.log("After Switches Filter:", devicesToFilter.length);
    } else if (state.groupTab === "fabricInterconnect") {
      devicesToFilter = devicesToFilter.filter(
        (device) => device["Inventory_Type"] === "Fabric Interconnect"
      );
      console.log("After Fabric Interconnect Filter:", devicesToFilter.length);
    } else if (state.groupTab === "storages") {
      devicesToFilter = devicesToFilter.filter(
        (device) => device["Inventory_Type"] === "Flash Array"
      );
      console.log("After Storage Filter:", devicesToFilter.length);
    }

   
    return devicesToFilter;
}, [state.devices, state.groupTab,state.activeTab]);

const filteredDevices = useMemo(() => {
    let devicesToDisplay = getFilteredDevices; 
    console.log("After getFilteredDevices:", devicesToDisplay.length);

    if (state.activeTab === "discovered" && state.searchInput) {
      devicesToDisplay = devicesToDisplay.filter((device) =>
        Object.values(device)
          .join(" ")
          .toLowerCase()
          .includes(state.searchInput.toLowerCase())
      );
      console.log("After Search Filter:", devicesToDisplay.length);
    }

    if (state.activeTagFilter && typeof state.activeTagFilter === "string") {
      devicesToDisplay = devicesToDisplay.filter((device) => {
        let tagsObj = {};
        try {
          const parsedTags = JSON.parse(device.Tags || "[]");

          if (Array.isArray(parsedTags)) {
            tagsObj = parsedTags.reduce((acc, tag) => {
              return { ...acc, ...JSON.parse(tag) };
            }, {});
          }

          const formattedTags = Object.entries(tagsObj)
            .map(([key, value]) => `${key}:${value}`)
            .join(", ");

          return formattedTags.toLowerCase().includes(state.activeTagFilter.toLowerCase());
        } catch (error) {
          console.error("Error parsing Tags for device:", device, error);
          return false;
        }
      });

      console.log("After Tag Filter:", devicesToDisplay.length);
    }

    console.log("Final Devices Displayed:", devicesToDisplay.length);
    return devicesToDisplay.slice(
      (state.currentPage - 1) * state.itemsPerPage,
      state.currentPage * state.itemsPerPage
    );
}, [
    state.devices,
    state.activeTab,
    state.searchInput,
    getFilteredDevices,
    state.activeTagFilter,
    state.currentPage,
    state.itemsPerPage,
]);


  
  
  const handleTagSelectionChange = useCallback(
    (tag) => {
      const newSelectedTags = new Set(state.selectedTags);
      if (newSelectedTags.has(tag.key)) {
        newSelectedTags.delete(tag.key);
      } else {
        newSelectedTags.add(tag.key);
      }
      localDispatch({ type: "SET_SELECTED_TAGS", payload: newSelectedTags });
    },
    [state.selectedTags]
  );

  const handleUpdateTags = useCallback(() => {
    if (state.selectedDeviceId) {
      const tagsArray = Array.from(state.selectedTags);
      const tagKeyValuePairs = tagsArray.reduce((acc, tagKey) => {
        const tag = tags.find((t) => t.key === tagKey);
        if (tag) {
          acc[tag.key] = tag.value;
        }
        return acc;
      }, {});
      console.log("Payload:", {
        ID: state.selectedDeviceId,
        Tag: tagKeyValuePairs,
      });
      handleTagAssign(state.selectedDeviceId, tagKeyValuePairs);
    }
    localDispatch({ type: "SET_TAGS_DROPDOWN_VISIBLE", payload: false });
  }, [state.selectedDeviceId, state.selectedTags, tags, handleTagAssign]);

  if (state.error) {
    return <div>Error: {state.error}</div>;
  }

  return (
    <div className="flex-1 flex flex-col min-h-[calc(100vh-100px)] p-4 md:p-6">
      {state.notification && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-green-100 text-green-800 px-4 py-2 rounded flex items-center shadow-lg z-50">
          <FaCheckCircle className="mr-2" />
          <span>{state.notification}</span>
        </div>
      )}
      
        <div className="absolute top-4 right-4 md:top-10 md:right-10 flex space-x-2 md:space-x-4">
          <button
            className="bg-[#fbb03b] text-white p-2 md:p-3 rounded-full shadow-md hover:scale-110 transition duration-200"
            onClick={toggleSearchVisibility}
          >
            <FaSearch className="text-lg md:text-xl" />
          </button>
          {state.searchVisible && (
            <input
              type="text"
              placeholder="Search devices..."
              value={state.searchInput}
              onChange={handleSearchInputChange}
              className="border px-2 py-1 md:px-3 md:py-2 mb-4 w-full max-w-[200px] md:max-w-xs"
            />
          )}
          <button
            className="bg-[#fbb03b] text-white p-2 md:p-3 rounded-full shadow-md hover:scale-110 transition duration-200"
            onClick={handleReload}
          >
            <FaSyncAlt className="text-lg md:text-xl" />
          </button>
        </div>

        <div className="w-full max-w-10xl px-0 md:px-4">
          <h1 className="text-xl md:text-2xl font-bold text-[#020a07] mb-2 md:mb-4 mt-4">
            Discovery
          </h1>
          <p className="text-sm md:text-base">
            Discovered Devices and Information View
          </p>
        </div>
        <div className="w-full max-w-10xl flex flex-col md:flex-row items-center justify-between bg-[#fbe3c1] py-2 md:py-4 px-0">
            <div className="flex">
              <button
                className={`px-4 md:px-6 py-1 md:py-2 ${
                  state.activeTab === "discovered"
                    ? "bg-orange-400 text-white"
                    : "bg-white"
                } border border-orange-400 rounded-l text-sm md:text-base`}
                onClick={setActiveTabToDiscovered}
              >
                Discovered Devices
              </button>
              <button
                className={`px-4 md:px-6 py-1 md:py-2 ${
                  state.activeTab === "grouping"
                    ? "bg-orange-400 text-white"
                    : "bg-white"
                } border border-orange-400 rounded-r text-sm md:text-base`}
                onClick={setActiveTabToGrouping}
              >
                Device Grouping
              </button>
            </div>
            <button
              onClick={handleHealthCheck}
              disabled={!state.selectedDeviceId}
              className={`mt-2 md:mt-0 px-3 md:px-4 py-1 md:py-2 rounded text-sm md:text-base ${
                state.selectedDeviceId
                  ? "bg-orange-400 text-white"
                  : "bg-orange-100 cursor-not-allowed"
              }`}
            >
              Check Health
            </button>
          </div>
        

        <div className="w-full max-w-10xl flex-1 h-full overflow-hidden px-2 lg:px-8">
        <div className="flex flex-col min-h-[calc(100vh-HEADER_HEIGHT)]">
          <div className="overflow-auto flex-grow sticky top-0 z-10 ">
            {state.activeTab === "discovered" && (
              <>
              <div className="w-full overflow-x-auto">
                <div className="md:max-h-[60vh] sm:max-h-[60vh] max-h-[60vh] overflow-y-auto border-t border-gray-300 xl:w-full w-full">
                  <table className="w-full text-left border-collapse">
                    <thead className="bg-orange-400 text-white sticky top-0 z-10">
                      <tr>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          <input
                            type="checkbox"
                            checked={state.selectAll}
                            onChange={handleSelectAllChange}
                            className="w-4 h-4"
                          />
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Serial ID
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Inventory Type
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Vendor Name
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          IP Address
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          DHCP Lease
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          DHCP Options
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Firmware Version
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Software Version
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Hardware Model
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Tags
                          <button
                            onClick={() => localDispatch({ type: "TOGGLE_TAG_FILTER_VISIBILITY" })}
                            className="ml-2"
                          >
                          <FaFilter />
                          </button>
                          {state.isTagFilterVisible && (
                            <div className="absolute bg-white text-black border mt-2 p-2">
                            {tags.map(({ key, value }) => (
                              <div
                                key={`${key}:${value}`} // Unique key
                                onClick={() => {
                                  localDispatch({ type: "SET_ACTIVE_TAG_FILTER", payload: `${key}:${value}` });
                                  localDispatch({ type: "TOGGLE_TAG_FILTER_VISIBILITY" });
                                }}
                                className="cursor-pointer hover:bg-gray-200 p-1"
                              >
                                {key}: {value}
                              </div>
                            ))}
                          </div>
                          
                          )}
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Health Status
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Action
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {state.loading ? (
                        <tr>
                          <td colSpan="10" className="text-center py-4">
                            Loading...
                          </td>
                        </tr>
                      ) : state.error ? (
                        <tr>
                          <td
                            colSpan="10"
                            className="text-center py-4 text-red-500"
                          >
                            Error: {state.error}
                          </td>
                        </tr>
                      ) : filteredDevices.length > 0 ? (
                        filteredDevices.map((device, index) => (
                          <tr
                            key={device.ID || index}
                            className={`${
                              index % 2 === 0 ? "bg-orange-100" : "bg-white"
                            }`}
                          >
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              <input
                                type="checkbox"
                                checked={state.selectedDeviceId === device.ID}
                                onChange={handleRowCheckboxChange.bind(
                                  null,
                                  device.ID
                                )}
                                className="w-4 h-4"
                              />
                              {state.tagsVisible &&
                                state.selectedRows.has(index) && (
                                  <div className="sticky z-10 top-[30px] mt-2 bg-white border border-gray-300 rounded shadow">
                                    <ul>
                                      {state.tagsLoading ? (
                                        <li className="p-2 text-gray-500 flex items-center space-x-2">
                                          <FaSpinner className="animate-spin text-orange-500" />
                                          <span>Loading tags...</span>
                                        </li>
                                      ) : tags.length > 0 ? (
                                        tags.map((tag) => (
                                          <li
                                            key={tag.key}
                                            className="p-2 hover:bg-gray-100 cursor-pointer"
                                          >
                                            <label>
                                              <input
                                                type="checkbox"
                                                checked={state.selectedTags.has(
                                                  tag.key
                                                )}
                                                onChange={handleTagSelectionChange.bind(
                                                  null,
                                                  tag
                                                )}
                                              />
                                              {tag.key}: {tag.value}
                                            </label>
                                          </li>
                                        ))
                                      ) : (
                                        <li className="p-2 text-gray-500">
                                          No tags available
                                        </li>
                                      )}
                                    </ul>
                                  </div>
                                )}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["Serial_ID"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["Inventory_Type"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["Vendor_Name"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["IP_Address"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["DHCP_Lease"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["DHCP_Options"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["Firmware_Version"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["Software_Version"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {device["Hardware_Model"] || "-"}
                            </td>
                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {(() => {
                                try {
                                  // Parse the JSON string safely
                                  const parsedTags = JSON.parse(device["Tags"] || "[]");

                                  // If it's an array, merge all objects into a single object
                                  if (Array.isArray(parsedTags)) {
                                    const mergedTags = parsedTags.reduce((acc, tag) => {
                                      return { ...acc, ...JSON.parse(tag) }; // Parse each string and merge
                                    }, {});

                                    // Convert the merged object into "key:value" format
                                    return Object.entries(mergedTags)
                                      .map(([key, value]) => `${key}:${value}`)
                                      .join(", ");
                                  }

                                  return "-"; // Default fallback
                                } catch (error) {
                                  console.error("Error parsing Tags:", error);
                                  return "-"; // In case of error, return "-"
                                }
                              })()}
                            </td>

                            <td className="border px-2 md:px-3 py-1 md:py-2">
                              {state.healthStatus[device.ID] ||
                                device["Status"]}
                            </td>
                            <td>
                              <div style={{ position: "relative" }}>
                                <button
                                  onClick={() => {
                                    localDispatch({
                                      type: "SET_SELECTED_DEVICE_ID",
                                      payload: device.ID,
                                    });
                                    localDispatch({
                                      type: "SET_TAGS_DROPDOWN_VISIBLE",
                                      payload: !state.tagsDropdownVisible,
                                    });
                                  }}
                                  
                                >
                                  ...
                                </button>
                                {state.tagsDropdownVisible &&
                                  state.selectedDeviceId === device.ID && (
                                    <div
                                      className="dropdown sticky bg-white shadow-md rounded-lg p-4 w-64 border border-gray-200 z-10"
                                      style={{ position: "absolute", right: 0 }}
                                    >
                                      <ul className="space-y-2">
                                        {state.tagsLoading ? (
                                          <li>Loading...</li>
                                        ) : (
                                          tags.map((tag) => (
                                            <li
                                              key={tag.key}
                                              className="flex items-center space-x-2"
                                            >
                                              <label>
                                                <input
                                                  type="checkbox"
                                                  className="w-3 h-3 text-orange-500 border-gray-300 rounded focus:ring-orange-400"
                                                  checked={state.selectedTags.has(
                                                    tag.key
                                                  )}
                                                  onChange={handleTagSelectionChange.bind(
                                                    null,
                                                    tag
                                                  )}
                                                />
                                                {tag.key}: {tag.value}
                                              </label>
                                            </li>
                                          ))
                                        )}
                                      </ul>
                                      <button
                                        onClick={handleUpdateTags}
                                        className="mt-4 w-full bg-gradient-to-r from-orange-400 to-orange-500 text-white font-medium py-2 rounded-lg hover:shadow-lg transition"
                                      >
                                        Update Tags
                                      </button>
                                    </div>
                                  )}
                              </div>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="10" className="text-center py-4">
                            No devices found.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                </div>
              </>
            )}
            {state.activeTab === "grouping" && (
              <div className="flex flex-col">
                <div className="sticky top-0 z-10 bg-[#fbe3c1]">
                  <div className="flex justify-center mb-4 p-4">
                    <button
                      className={`px-4 py-2 ${
                        state.groupTab === "switches"
                          ? "bg-orange-400 text-white"
                          : "bg-white"
                      } border border-orange-400 rounded-l`}
                      onClick={setGroupTabToSwitches}
                    >
                      Switches
                    </button>
                    <button
                      className={`px-4 py-2 ${
                        state.groupTab === "fabricInterconnect"
                          ? "bg-orange-400 text-white"
                          : "bg-white"
                      } border border-orange-400`}
                      onClick={setGroupTabToFabric}
                    >
                      Fabric Interconnect
                    </button>
                    <button
                      className={`px-4 py-2 ${
                        state.groupTab === "storages"
                          ? "bg-orange-400 text-white"
                          : "bg-white"
                      } border border-orange-400 rounded-r`}
                      onClick={setGroupTabToStorages}
                    >
                      Storages
                    </button>
                  </div>
                  <h2 className="text-xl font-bold mb-4 px-4">
                    {state.groupTab} Devices
                  </h2>
                </div>
                <div className="w-full overflow-x-auto">
                <div className="md:max-h-[40vh] max-h-[40vh] overflow-y-auto border-t border-gray-300 xl:w-full w-full">
                  <table className="table-auto w-full text-left border-collapse">
                    <thead className="bg-orange-400 text-white sticky top-0">
                      <tr>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          <input
                            type="checkbox"
                            checked={state.selectAll}
                            onChange={handleSelectAllChange}
                            className="w-4 h-4"
                          />
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Serial ID
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Inventory Type
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Vendor Name
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          IP Address
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          DHCP Lease
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          DHCP Options
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Firmware Version
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Software Version
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Hardware Model
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Tags
                        </th>
                        <th className="border px-2 md:px-3 py-1 md:py-2">
                          Health Status
                        </th>
                        
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredDevices.map((device, index) => (
                        <tr
                          key={index}
                          className={`${
                            index % 2 === 0 ? "bg-orange-100" : "bg-white"
                          }`}
                        >
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            <input
                              type="checkbox"
                              checked={state.selectedDeviceId === device.ID}
                              onChange={handleRowCheckboxChange.bind(
                                null,
                                device.ID
                              )}
                              className="w-4 h-4"
                            />
                            {state.tagsVisible &&
                              state.selectedRows.has(index) && (
                                <div className="sticky z-10 top-[30px] mt-2 bg-white border border-gray-300 rounded shadow">
                                  <ul>
                                    {state.tagsLoading ? (
                                      <li className="p-2 text-gray-500 flex items-center space-x-2">
                                        <FaSpinner className="animate-spin text-orange-500" />
                                        <span>Loading tags...</span>
                                      </li>
                                    ) : tags.length > 0 ? (
                                      tags.map((tag) => (
                                        <li
                                          key={tag.key}
                                          className="p-2 hover:bg-gray-100 cursor-pointer"
                                        >
                                          <label>
                                            <input
                                              type="checkbox"
                                              checked={state.selectedTags.has(
                                                tag.key
                                              )}
                                              onChange={handleTagSelectionChange.bind(
                                                null,
                                                tag
                                              )}
                                            />
                                            {tag.key}: {tag.value}
                                          </label>
                                        </li>
                                      ))
                                    ) : (
                                      <li className="p-2 text-gray-500">
                                        No tags available
                                      </li>
                                    )}
                                  </ul>
                                </div>
                              )}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["Serial_ID"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["Inventory_Type"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["Vendor_Name"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["IP_Address"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["DHCP_Lease"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["DHCP_Options"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["Firmware_Version"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["Software_Version"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {device["Hardware_Model"] || "-"}
                          </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                              {(() => {
                                try {
                                  // Parse the JSON string safely
                                  const parsedTags = JSON.parse(device["Tags"] || "[]");

                                  // If it's an array, merge all objects into a single object
                                  if (Array.isArray(parsedTags)) {
                                    const mergedTags = parsedTags.reduce((acc, tag) => {
                                      return { ...acc, ...JSON.parse(tag) }; // Parse each string and merge
                                    }, {});

                                    // Convert the merged object into "key:value" format
                                    return Object.entries(mergedTags)
                                      .map(([key, value]) => `${key}:${value}`)
                                      .join(", ");
                                  }

                                  return "-"; // Default fallback
                                } catch (error) {
                                  console.error("Error parsing Tags:", error);
                                  return "-"; // In case of error, return "-"
                                }
                              })()}
                            </td>
                          <td className="border px-2 md:px-3 py-1 md:py-2">
                            {state.healthStatus[device.ID] || device["Status"]}
                          </td>
                          
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="w-full max-w-10xl flex flex-row items-center justify-between bg-[#fbe3c1] py-4 px-4">
          <div>
            <label htmlFor="itemsPerPage" className=""></label>
            <select id="itemsPerPage" className="border rounded px-2 py-1 bg-orange-400 text-white hover:bg-orange-500 transition" value={state.itemsPerPage} onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={30}>30</option>
              <option value={50}>50</option>
            </select>
          </div>
          <div className="flex space-x-2 items-center">
            <button className="w-8 h-8 bg-orange-400 text-white rounded-full flex items-center justify-center hover:bg-orange-500 transition" onClick={handlePreviousPage}>❮</button>
            <button className="w-8 h-8 bg-orange-400 text-white rounded-full flex items-center justify-center hover:bg-orange-500 transition" onClick={handleNextPage} disabled={state.currentPage === totalPages}>❯</button>
          </div>
        </div>
      </div>
      
    </div>
  );
};

export default Discovery;
