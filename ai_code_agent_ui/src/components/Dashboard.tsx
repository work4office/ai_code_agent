import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";
import useApi from "../hooks/useApi";
import { useAuth } from "../context/AuthContext";
import { Loader } from "./Loader";

export default function Dashboard() {
  const { get_all_projects } = useApi();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isLoading } = useAuth();

  const toggleSidebar = async () => {
    await get_all_projects();
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar Integration */}
      <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} />

      {/* Main Framework Box */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <Header toggleSidebar={toggleSidebar} />

        {/* Scrollable Viewport Arena */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
      <Loader isLoading={isLoading} />
    </div>
  );
}
