import React from "react";
import { useAuth } from "../context/AuthContext";
import { Link, useNavigate } from "react-router-dom";
import { useCommonContext } from "../context/CommonContext";
import useApi from "../hooks/useApi";
import type { SidebarProps } from "../types/common.types";

export default function Sidebar({ isOpen, toggleSidebar }: SidebarProps) {
  const { user } = useAuth();
  const { activeProject, setActiveProject, projects } = useCommonContext();
  const navigate = useNavigate();
  const { get_file_tree } = useApi();

  const selectProject = async (projectId: string) => {
    setActiveProject(projectId);
    await get_file_tree(projectId);
    navigate("/editor");
    if (toggleSidebar) {
      toggleSidebar();
    }
  };

  return (
    <>
      {isOpen && (
        <aside
          className={`
        fixed inset-y-0 left-0 z-30 w-64 bg-[#0d0e12] text-white p-5 transform transition-transform duration-300 ease-in-out
        lg:translate-x-0 lg:static lg:inset-auto
        ${isOpen ? "translate-x-0" : "-translate-x-0 max-lg:-translate-x-full"}
      `}
        >
          {/* Sidebar Header / Logo */}
          <div className="flex items-center justify-between pb-6 border-b border-slate-700">
            {user ? (
              <span className="capitalize text-xl font-bold tracking-wider">
                Repositories
              </span>
            ) : (
              <span className="hidden md:inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium text-white border border-gray-200 rounded-full hover:bg-white hover:text-[#0d0e12] transition-colors duration-200 cursor-pointer">
                <Link to="/signIn">Log In</Link>
              </span>
            )}
            <button
              onClick={toggleSidebar}
              className="cursor-pointer text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="mt-6 space-y-2">
            {projects?.map((project) => (
              <div
                onClick={() => selectProject(project.project_id)}
                key={project.project_id}
                className={`cursor-pointer flex items-center gap-3 px-4 py-2.5 rounded-lg font-medium 
                  ${
                    activeProject === project?.project_id
                      ? "bg-white text-[#0d0e12]"
                      : "text-white hover:bg-white hover:text-[#0d0e12] transition"
                  }`}
              >
                {project.repo_name}
              </div>
            ))}

            {/* <a
              href="#"
              className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-400 hover:bg-slate-800 hover:text-white transition"
            >
              Settings
            </a> */}
          </nav>
        </aside>
      )}
    </>
  );
}
