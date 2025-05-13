import React, { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import Header from "../components/Header";
import { toast } from "react-toastify";

const InstructorProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("Access token not found");

      const decoded = jwtDecode(token);
      const instructorId = decoded.sub;

      const response = await fetch(
        `http://localhost:8000/api/instructors/${instructorId}/profile`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch profile");
      }

      const data = await response.json();
      setProfile(data);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  if (loading) return (
    <>
    <Header />
    <p className="text-center mt-8">Loading profile...</p>;
    </>
  )
  if (!profile) return (
    <>
    <Header />
    <p className="text-red-500 text-center mt-8">Failed to fetch profile</p>;
    </>
  )

  return (
    <>
      <Header />
      <div className="flex justify-center h-screen bg-gray-50 px-4">
        <div className="w-full max-w-3xl mx-auto p-6">
            <h2 className="text-3xl font-bold text-center text-blue-800 mb-8">
            My profile
            </h2>

            <div className="bg-white shadow-xl rounded-lg p-6 border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                <p className="text-gray-600 font-semibold">Last Name:</p>
                <p className="text-lg">{profile.last_name}</p>
                </div>
                <div>
                <p className="text-gray-600 font-semibold">First Name:</p>
                <p className="text-lg">{profile.first_name}</p>
                </div>
                <div>
                <p className="text-gray-600 font-semibold">Patronymic:</p>
                <p className="text-lg">{profile.patronymic}</p>
                </div>
                <div>
                <p className="text-gray-600 font-semibold">Username:</p>
                <p className="text-lg">{profile.username}</p>
                </div>
                <div>
                <p className="text-gray-600 font-semibold">Phone Number:</p>
                <p className="text-lg">{profile.phone_number}</p>
                </div>
                <div>
                <p className="text-gray-600 font-semibold">Birthday:</p>
                <p className="text-lg">{profile.birthday}</p>
                </div>
                <div>
                <p className="text-gray-600 font-semibold">Work Started:</p>
                <p className="text-lg">{profile.work_started_date}</p>
                </div>
            </div>

            <div className="mt-6">
                <h3 className="text-xl font-bold mb-4 text-blue-700">
                Category Levels
                </h3>
                <div className="max-h-[300px] overflow-y-auto overflow-x-auto">
                <table className="min-w-full bg-gray-50 rounded-md overflow-hidden shadow border">
                    <thead className="bg-blue-600 text-white">
                    <tr>
                        <th className="px-4 py-3 text-left">Category</th>
                        <th className="px-4 py-3 text-left">Transmission</th>
                    </tr>
                    </thead>
                    <tbody>
                    {profile.categories.map((cat, index) => (
                        <tr
                        key={index}
                        className={index % 2 === 0 ? "bg-white" : "bg-gray-100"}
                        >
                        <td className="px-4 py-3">{cat.category}</td>
                        <td className="px-4 py-3">{cat.transmission}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
                </div>
            </div>
            </div>
        </div>
      </div>
    </>
  );
};

export default InstructorProfile;
