import React, { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import Header from "../components/Header";
import { toast } from "react-toastify";

const AdminProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editAdmin, setEditAdmin] = useState(null);

  const token = localStorage.getItem("access_token");

  const decoded = jwtDecode(token);
  const adminId = decoded.sub;

  const fetchProfile = async () => {
    try {
      if (!token) throw new Error("Access token not found");

      const response = await fetch(
        `http://localhost:8000/api/admins/${adminId}/profile`,
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
  }, [token]);

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setEditAdmin((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditClick = () => {
    setEditAdmin({
      ...profile,
    });
    setIsEditModalOpen(true);
  };

  const handleEditAdmin = async () => {
      const payload = {
          user: {
              username: editAdmin.username.trim(),
              first_name: editAdmin.first_name.trim(),
              last_name: editAdmin.last_name.trim(),
              patronymic: editAdmin.patronymic.trim() === "" ? null : editAdmin.patronymic.trim(),
              birthday: editAdmin.birthday,
              phone_number: editAdmin.phone_number.trim(),
          },
          password: null,
      };
  
      try {
        const res = await fetch(`http://localhost:8000/api/admins/${adminId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });
  
        const data = await res.json();
        if (!res.ok) {
          if (res.status === 422) {
            const messages = data.detail.map(
              (err) => `${err.loc.slice(1).join(".")}: ${err.msg}`
            );
              throw new Error(messages.join("\n"));
          } else {
            throw new Error(data.detail);
          }
        }
  
        await fetchProfile();
        setIsEditModalOpen(false);
        toast.success("Admin`s data changed")
      } catch (error) {
        toast.error(error.message);
      }
    };

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
            Admin Profile
            </h2>

            <div className="flex justify-center mb-6">
                <button
                    onClick={handleEditClick}
                    className="px-5 py-3 bg-yellow-500 text-white rounded hover:bg-yellow-600 font-semibold"
                    >
                    Edit
                </button>
            </div>

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
            </div>
            </div>

            {isEditModalOpen && editAdmin && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-700">Edit admin</h3>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">First name</label>
                        <input
                            type="text"
                            name="first_name"
                            value={editAdmin.first_name}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Last name</label>
                        <input
                            type="text"
                            name="last_name"
                            value={editAdmin.last_name}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Patronymic</label>
                        <input
                            type="text"
                            name="patronymic"
                            value={editAdmin.patronymic}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Birthday</label>
                        <input
                            type="date"
                            name="birthday"
                            value={editAdmin.birthday}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Phone number</label>
                        <input
                            type="text"
                            name="phone_number"
                            value={editAdmin.phone_number}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                  <div className="flex justify-end gap-3 mt-6">
                    <button
                      onClick={() => setIsEditModalOpen(false)}
                      className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleEditAdmin}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Save
                    </button>
                  </div>

                </div>
            </div>
            )}

        </div>
      </div>
    </>
  );
};

export default AdminProfile;
