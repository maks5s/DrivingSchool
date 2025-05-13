import React, { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import Header from "../components/Header";
import { toast } from "react-toastify";

const StudentProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("Access token not found");

      const decoded = jwtDecode(token);
      const studentId = decoded.sub;

      const response = await fetch(
        `http://localhost:8000/api/students/${studentId}/profile`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch student profile");
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
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
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
                <p className="text-gray-600 font-semibold">Category:</p>
                <p className="text-lg">{profile.category}</p>
                </div>
                <div>
                <p className="text-gray-600 font-semibold">Transmission:</p>
                <p className="text-lg">{profile.transmission}</p>
                </div>
                <div>
                <p className="text-gray-600 font-semibold">Group:</p>
                <p className="text-lg">{profile.group}</p>
                </div>
            </div>
            </div>
        </div>
      </div>
    </>
  );
};

export default StudentProfile;
