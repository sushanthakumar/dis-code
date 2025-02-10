import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import { useDispatch } from "react-redux";
import Sidebar from "./components/sideBar";
import Discovery from "./pages/discovery";
import Recommend from "./pages/recommendations";
import Settings from "./pages/settings";
import Usecases from "./pages/usecase";
import DhcpServer from "./pages/DhcpServer";
import DhcpHost from "./pages/DhcpHost";
import AddDevices from "./pages/AddDevices";
import { fetchTags } from "./store/store";
import { ToastContainer } from "react-toastify"; // Import ToastContainer
import "react-toastify/dist/ReactToastify.css"; // Import toast styles

const App = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(fetchTags());
  }, [dispatch]);

  return (
    <div className="flex h-screen bg-[#FBE7CC]">
      <Sidebar className="h-full" />
      <div className="flex-1 h-full overflow-hidden">
        <Routes>
          <Route path="/" element={<Discovery />} />
          <Route path="/recommend" element={<Recommend />} />
          <Route path="/settings/Tags" element={<Settings />} />
          <Route path="/settings/usecase" element={<Usecases />} />
          <Route path="/settings/dhcp" element={<DhcpServer />} />
          <Route path="/settings/DhcpHost" element={<DhcpHost />} />
          <Route path="/settings/AddDevices" element={<AddDevices />} />
        </Routes>
      </div>
      {/* Add ToastContainer here to show toast notifications globally */}
      <ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} />
    </div>
  );
};

export default App;
