import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { toast } from "react-toastify";

const AdminCabinetsList = () => {
  const [loading, setLoading] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [cabinets, setCabinets] = useState([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newCabinet, setNewCabinet] = useState({
    name: "",
  });
  const [selectedCabinet, setSelectedCabinet] = useState(null);

  const token = localStorage.getItem("access_token");

  const fetchCabinets = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/cabinets/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setCabinets(data);
    } catch (error) {
      toast.error("Error fetching cabinets:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCabinets();
  }, [token]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCabinet((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setSelectedCabinet((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditClick = (cab) => {
    setSelectedCabinet({
      ...cab,
    });
    setIsEditModalOpen(true);
  };

  const handleEditCabinet = async () => {
    const payload = {
      name: selectedCabinet.name.trim(),
    };

    try {
      const res = await fetch(`http://localhost:8000/api/cabinets/${selectedCabinet.id}`, {
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

      await fetchCabinets();
      setIsEditModalOpen(false);
      toast.success("Cabinet`s data changed")
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleAddClick = () => {
    setNewCabinet({
      name: "",
    });
    setIsAddModalOpen(true);
  };

  const handleAddCabinet = async () => {
    const payload = {
      name: newCabinet.name.trim(),
    };

    try {
      const res = await fetch("http://localhost:8000/api/cabinets/", {
        method: "POST",
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

      await fetchCabinets();
      setIsAddModalOpen(false)
      toast.success("Cabinet added")
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <>
      <Header />
      <div className="flex justify-center bg-gray-50 px-4 h-screen">
        <div className="w-full max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold text-center text-blue-800 mb-4">Cabinets List</h2>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-1 gap-4 mb-4">

              <div className="flex justify-center">
                <button
                    onClick={() => handleAddClick(true)}
                    className="px-5 py-3 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                    Add cabinet
                </button>
              </div>

            </div>
          </div>

            <div className="max-h-[500px] overflow-y-auto overflow-x-auto rounded-lg shadow-lg border border-gray-200 bg-white">
              <table className="min-w-full bg-gray-50 rounded-md shadow border">
                <thead className="bg-blue-600 text-white sticky top-0 z-10">
                  <tr>
                    <th className="px-4 py-3 text-left">Name</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {cabinets.map((cab, idx) => (
                    <tr key={cab.id} className={idx % 2 === 0 ? "bg-white" : "bg-gray-100"}>
                      <td className="px-4 py-3">{cab.name}</td>
                      <td className="px-4 py-3">
                        <button
                            onClick={() => handleEditClick(cab)}
                            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                        >
                            Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          {loading && <p className="text-center mt-6">Loading cabinets...</p>}

          {isAddModalOpen  && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                  <h3 className="text-xl font-bold mb-4 text-blue-700">Add cabinet</h3>
                  <div>
                    <label className="block font-semibold text-gray-700 mb-1">Name</label>
                    <input
                    type="text"
                    name="name"
                    value={newCabinet.name}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                    />
                  </div>

                  <div className="flex justify-end gap-3 mt-6">
                    <button
                      onClick={() => setIsAddModalOpen(false)}
                      className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleAddCabinet}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Add
                    </button>
                  </div>
                </div>
            </div>
          )}

          {isEditModalOpen && selectedCabinet && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-700">Edit cabinet</h3>

                <div>
                    <label className="block font-semibold text-gray-700 mb-1">Name</label>
                    <input
                    type="text"
                    name="name"
                    value={selectedCabinet.name}
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
                        onClick={handleEditCabinet}
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

export default AdminCabinetsList;
