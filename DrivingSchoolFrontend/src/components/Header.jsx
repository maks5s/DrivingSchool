import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

const Header = () => {
  const navigate = useNavigate();

  const token = localStorage.getItem("access_token");
  let role = null;

  if (token) {
    try {
      const decoded = jwtDecode(token);
      role = decoded.role;
    } catch (error) {
      console.error("Invalid token");
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const baseButtonClasses =
    "px-4 py-2 rounded-lg transition font-medium";
  const activeClasses = "bg-white text-blue-700";
  const inactiveClasses = "bg-blue-500 hover:bg-blue-600 text-white";

  return (
    <header className="bg-blue-700 text-white shadow-md p-4 flex justify-between items-center px-6">
      <h1 className="text-xl font-semibold tracking-wide">Driving School</h1>
      <nav className="flex space-x-4 items-center">
        {role === "student_role" && (
          <>
            <NavLink
              to="/student/schedule"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Schedule
            </NavLink>
            <NavLink
              to="/student/profile"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Profile
            </NavLink>
          </>
        )}
        {role === "instructor_role" && (
          <>
            <NavLink
              to="/instructor/schedule"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Schedule
            </NavLink>
            <NavLink
              to="/instructor/profile"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Profile
            </NavLink>
          </>
        )}
        {role === "admin_role" && (
          <>
            <NavLink
              to="/admin/schedule"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Schedule
            </NavLink>
            <NavLink
              to="/admin/instructors"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Instructors
            </NavLink>
            <NavLink
              to="/admin/groups"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Groups
            </NavLink>
            <NavLink
              to="/admin/students"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Students
            </NavLink>
            <NavLink
              to="/admin/category_levels"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Cat. Levels
            </NavLink>
            <NavLink
              to="/admin/vehicles"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Vehicles
            </NavLink>
            <NavLink
              to="/admin/cabinets"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Cabinets
            </NavLink>
            <NavLink
              to="/admin/statistics"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Statistics
            </NavLink>
            <NavLink
              to="/admin/data"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Data
            </NavLink>
            <NavLink
              to="/admin/profile"
              className={({ isActive }) =>
                `${baseButtonClasses} ${
                  isActive ? activeClasses : inactiveClasses
                }`
              }
            >
              Profile
            </NavLink>
          </>
        )}
        <button
          onClick={handleLogout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition font-medium"
        >
          Logout
        </button>
      </nav>
    </header>
  );
};

export default Header;
