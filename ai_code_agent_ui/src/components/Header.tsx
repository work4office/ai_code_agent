import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getInitials } from "../utils/commonFunctions";
import { useCommonContext } from "../context/CommonContext";

interface HeaderProps {
  toggleSidebar: () => void;
}

export default function Header({ toggleSidebar }: HeaderProps) {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const { resetContext } = useCommonContext();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close the dropdown when clicking outside of it
  useEffect(() => {
    function handleClickOutside(event: any) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const logOut = async () => {
    await logout();
    setIsOpen(false);
    navigate("/");
    resetContext();
  };
  return (
    <header className="flex items-center justify-between bg-white border-b border-gray-200 h-16 px-6">
      {/* Profile & Notifications Actions */}
      <div className="flex items-center hidden md:inline text-sm font-medium text-gray-700 cursor-pointer">
        <button
          onClick={toggleSidebar}
          className="cursor-pointer p-2 -ml-2 text-gray-600 rounded-md hover:bg-gray-100"
        >
          ☰
        </button>
        <Link to="/">Ai Code Agent</Link>
      </div>
      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-2">
            <div className="relative inline-block text-left" ref={dropdownRef}>
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="cursor-pointer inline-flex w-full justify-center gap-x-1.5 rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 transition-all duration-200"
                aria-expanded={isOpen}
                aria-haspopup="true"
              >
                {getInitials(user.name)}
              </button>
              {isOpen && (
                <div className="absolute right-0 z-10 mt-2 w-40 origin-top-right rounded-md bg-white shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none">
                  <div className="py-1" role="menu" aria-orientation="vertical">
                    <a
                      href="#account"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                      role="menuitem"
                    >
                      Account settings
                    </a>
                    <hr className="my-1 border-gray-100" />
                    <button
                      type="submit"
                      className="block w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 font-medium"
                      role="menuitem"
                      onClick={logOut}
                    >
                      Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>

            <span className="capitalize hidden md:inline text-sm font-medium text-gray-700">
              {user.name}
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link
              to="/signUp"
              className="hidden md:inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium text-gray-900 border border-gray-200 rounded-full hover:bg-gray-100 transition-colors duration-200 cursor-pointer"
            >
              SignUp
            </Link>

            <Link
              to="/signIn"
              className="hidden md:inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium text-gray-900 border border-gray-200 rounded-full hover:bg-gray-100 transition-colors duration-200 cursor-pointer"
            >
              SignIn
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
