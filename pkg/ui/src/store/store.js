/*
Project name : SmartConfigNxt
Title : store.jsx
Description : Manages Redux state with slices..
Author :  Caze Labs
version :1.0 
*/

import { configureStore, createSlice } from "@reduxjs/toolkit";
const deviceSlice = createSlice({
  name: "devices",
  initialState: [],
  reducers: {
    setDevices: (state, action) => action.payload,
  },
});


const tagsSlice = createSlice({
  name: "tags",
  initialState: [],
  reducers: {
    addTag: (state, action) => {
      return [...state, action.payload];
    },

    deleteTag: (state, action) => {
      return state.filter((tag) => tag.id !== action.payload);
    },
    setTags: (state, action) => action.payload,
  },
});


export const fetchTags = () => async (dispatch) => {
  const CACHE_DURATION = 5 * 60 * 1000;
  const cacheKey = "tagsCache";

  const cachedData = localStorage.getItem(cacheKey);
  if (cachedData) {
    const { timestamp, data } = JSON.parse(cachedData);
    if (Date.now() - timestamp < CACHE_DURATION) {

      dispatch(setTags(data));

    }
  }
  try {
    const response = await fetch("http://127.0.0.1:5000/v1/customtags");
    if (!response.ok) {
      throw new Error("Failed to fetch tags.");
    }
    const data = await response.json();

    const transformedTags = data.map((item) => {
      const tagObject = item[1] || {};
      const key = Object.keys(tagObject).find((key) => key.trim()) || "";
      const value = tagObject[key] || "";
      return {
        id: item[0]?.Id,
        key,
        value,
      };
    });
    localStorage.setItem(
      cacheKey,
      JSON.stringify({ timestamp: Date.now(), data: transformedTags })
    );
    dispatch(setTags(transformedTags));
  } catch (error) {
    console.error("Error fetching tags:", error);
  }
};


export const { setDevices } = deviceSlice.actions;
export const { addTag, deleteTag, setTags } = tagsSlice.actions;


const store = configureStore({
  reducer: {
    devices: deviceSlice.reducer,
    tags: tagsSlice.reducer,
  },
});

export default store;
