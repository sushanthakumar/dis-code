import React, { useState, useCallback, useMemo } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  ChevronDown,
  ChevronUp,
  Settings,
  Home,
  FileText,
  Tag,
  List,
  Server,
  Upload,
  ServerCog,
  Menu,
  X
} from "lucide-react";
import Logo1 from "../assets/SCN Logo.png";
import Logo2 from "../assets/Picture1.png";

const Sidebar = () => {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Sidebar visibility state
  const location = useLocation();

  const toggleSettings = useCallback(() => {
    setSettingsOpen((prev) => !prev);
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  const isActive = useMemo(() => (path) => location.pathname === path, [location.pathname]);
  const isSettingsActive = useMemo(() => location.pathname.startsWith("/settings"), [location.pathname]);

  const discoveryClass = useMemo(
    () => `hover:underline font-bold flex items-center px-4 py-2 rounded-lg ${isActive("/") ? "bg-orange-600" : ""}`,
    [isActive, location.pathname]
  );

  const recommendClass = useMemo(
    () => `hover:underline font-bold flex items-center px-4 py-2 rounded-lg ${isActive("/recommend") ? "bg-orange-600" : ""}`,
    [isActive, location.pathname]
  );

  const settingsClass = useMemo(
    () => `w-full text-left font-bold flex items-center px-4 py-2 rounded-lg ${isSettingsActive ? "bg-orange-600" : ""}`,
    [isSettingsActive]
  );

  return (
    <div>
      
      <button onClick={toggleSidebar} className="md:hidden fixed top-4 left-4 z-50 bg-orange-600 p-2 rounded-lg">
        {isSidebarOpen ? <X size={24} className="text-white" /> : <Menu size={24} className="text-white" />}
      </button>

      
      <div
        className={`fixed md:relative top-0 left-0 min-h-screen bg-orange-500 text-white flex flex-col items-center p-2 rounded-tr-2xl rounded-br-2xl shadow-lg transition-transform duration-300 ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
        style={{ width: "220px" }}
      >
        <h1 className="text-2xl pt-4 pb-6 font-bold">SmartConfigNXT</h1>
        <img src={Logo1} alt="SmartConfig Logo" className="w-20 h-20 mb-4 rounded-full border-4 border-white" loading="lazy" />

       
        <nav className="flex flex-col md:space-y-2 lg:space-y-4 xl:space-y-2 pt-6 w-full">
          <Link to="/" className={discoveryClass}>
            <Home className="mr-2" /> Discovery
          </Link>

          <Link to="/recommend" className={recommendClass}>
            <FileText className="mr-1" /> Recommendations
          </Link>

          
          <div className="w-full mb-2">
            <button onClick={toggleSettings} className={settingsClass}>
              <Settings className="mr-2" />
              Settings
              {settingsOpen ? <ChevronUp className="ml-auto" /> : <ChevronDown className="ml-auto" />}
            </button>

            {settingsOpen && (
              <div className="pl-6 pr-1 space-y-2 mt-2 md:max-h-20 overflow-y-auto scrollbar-thin scrollbar-thumb-orange-500 scrollbar-track-orange-400">
                <Link to="/settings/Tags" className={`hover:underline flex items-center px-2 py-1 rounded-lg ${isActive("/settings/Tags") ? "bg-orange-600" : ""}`}>
                  <Tag className="mr-2" /> Tags
                </Link>
                <Link to="/settings/usecase" className={`hover:underline flex items-center px-2 py-1 rounded-lg ${isActive("/settings/usecase") ? "bg-orange-600" : ""}`}>
                  <List className="mr-2" /> Use Cases
                </Link>
                <Link to="/settings/dhcp" className={`hover:underline flex items-center px-2 py-1 rounded-lg ${isActive("/settings/dhcp") ? "bg-orange-600" : ""}`}>
                  <Server className="mr-2" /> DHCP Server
                </Link>
                <Link to="/settings/DhcpHost" className={`hover:underline flex items-center px-2 py-1 rounded-lg ${isActive("/settings/DhcpHost") ? "bg-orange-600" : ""}`}>
                  <ServerCog className="mr-2" /> DHCP Host
                </Link>
                <Link to="/settings/AddDevices" className={`hover:underline flex items-center px-2 py-1 rounded-lg ${isActive("/settings/AddDevices") ? "bg-orange-600" : ""}`}>
                  <Upload className="mr-2" /> Add Devices
                </Link>
              </div>
            )}
          </div>
        </nav>

        
        <footer className="mt-auto text-sm flex flex-col items-center space-y-2">
          <h4 className="mt-3">Ver 0.1.0</h4>
          <img src={Logo2} alt="Footer Logo" className="w-25 h-20 md:w-20 md:h-20" loading="lazy" />
        </footer>
      </div>

      
      {isSidebarOpen && (
        <div className="fixed inset-0 bg-black opacity-50 md:hidden" onClick={toggleSidebar}></div>
      )}
    </div>
  );
};

export default React.memo(Sidebar);
