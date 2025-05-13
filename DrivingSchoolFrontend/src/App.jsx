import { RouterProvider, createBrowserRouter } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import LoginPage from "./pages/LoginPage";
import "../src/index.css";
import StudentProfile from "./pages/StudentProfile";
import PrivateRoute from "./components/PrivateRoute";
import StudentSchedule from "./pages/StudentSchedule";
import InstructorSchedule from "./pages/InstructorSchedule";
import InstructorProfile from "./pages/InstructorProfile";
import AdminProfile from "./pages/AdminProfile";
import AdminScheduleViewer from "./pages/AdminScheduleViewer";
import AdminInstructorsList from "./pages/AdminInstructorsList";
import AdminCategoryLevelsList from "./pages/AdminCategoryLevelsList";
import AdminVehicleList from "./pages/AdminVehicleList";
import AdminCabinetsList from "./pages/AdminCabinetsList";
import AdminGroupsList from "./pages/AdminGroupsList";
import AdminStudentsList from "./pages/AdminStudentsList";
import AdminStatisticsPage from "./pages/AdminStatisticsPage";
import AdminDataUploadPage from "./pages/AdminDataUploadPage";

const router = createBrowserRouter([
  { path: "/student/profile", element: 
  <PrivateRoute>
    <StudentProfile /> 
  </PrivateRoute>
  },
  { path: "/instructor/profile", element: 
    <PrivateRoute>
      <InstructorProfile /> 
    </PrivateRoute>
  },
  { path: "/instructor/schedule", element: 
    <PrivateRoute>
      <InstructorSchedule /> 
    </PrivateRoute>
  },
  { path: "/student/schedule", element: 
    <PrivateRoute>
      <StudentSchedule /> 
    </PrivateRoute>
  },
  { path: "/admin/schedule", element: 
    <PrivateRoute>
      <AdminScheduleViewer /> 
    </PrivateRoute>
  },
  { path: "/admin/profile", element: 
    <PrivateRoute>
      <AdminProfile /> 
    </PrivateRoute>
  },
  { path: "/admin/instructors", element: 
    <PrivateRoute>
      <AdminInstructorsList /> 
    </PrivateRoute>
  },
  { path: "/admin/category_levels", element: 
    <PrivateRoute>
      <AdminCategoryLevelsList /> 
    </PrivateRoute>
  },
  { path: "/admin/vehicles", element: 
    <PrivateRoute>
      <AdminVehicleList /> 
    </PrivateRoute>
  },
  { path: "/admin/cabinets", element: 
    <PrivateRoute>
      <AdminCabinetsList /> 
    </PrivateRoute>
  },
  { path: "/admin/groups", element: 
    <PrivateRoute>
      <AdminGroupsList /> 
    </PrivateRoute>
  },
  { path: "/admin/students", element: 
    <PrivateRoute>
      <AdminStudentsList /> 
    </PrivateRoute>
  },
  { path: "/admin/statistics", element: 
    <PrivateRoute>
      <AdminStatisticsPage /> 
    </PrivateRoute>
  },
  { path: "/admin/data", element: 
    <PrivateRoute>
      <AdminDataUploadPage /> 
    </PrivateRoute>
  },
  { path: "/login", element: <LoginPage /> },
]);

function App() {
  return (
    <>
      <RouterProvider className={"content"} router={router} />;
      <ToastContainer />
    </>
  )
}

export default App
