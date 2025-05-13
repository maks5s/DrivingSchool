import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { toast } from "react-toastify";
import Select from "react-select";

const AdminVehicleList = () => {
  const [loading, setLoading] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [vehicles, setVehicles] = useState([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newVehicle, setNewVehicle] = useState({
    brand: "",
    model: "",
    manufacture_year: 2010,
    license_plate: "",
    fuel_type: "",
    category_level_id: 0,
  });
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryLevelId, setCategoryLevelId] = useState(null);
  const [pageSize, setPageSize] = useState(10);
  const [categoryOptions, setCategoryOptions] = useState([]);

  const token = localStorage.getItem("access_token");

  const fetchCategoryLevels = async () => {
    try {
        const res = await fetch("http://localhost:8000/api/category_levels/", {
        headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setCategoryOptions(
        data.map((c) => ({
            value: c.id,
            label: `${c.category} ${c.transmission}`,
        }))
        );
    } catch (err) {
        toast.error("Failed to fetch category levels");
    }
    };

  const fetchVehicles = async () => {
    setLoading(true);
    try {
      const url = new URL("http://localhost:8000/api/vehicles/paginated");
      url.searchParams.append("page", page);
      url.searchParams.append("page_size", pageSize);
      if (categoryLevelId) url.searchParams.append("category_level_id", categoryLevelId);
      if (searchTerm) url.searchParams.append("search", searchTerm);
    
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setVehicles(data);
    } catch (error) {
      toast.error("Error fetching vehicles:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategoryLevels()
    fetchVehicles();
  }, [token]);

  useEffect(() => {
    fetchVehicles();
  }, [page, categoryLevelId, pageSize, searchTerm]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewVehicle((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setSelectedVehicle((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditClick = (vehicle) => {
    setSelectedVehicle({
      ...vehicle,
    });
    setIsEditModalOpen(true);
  };

  const handleEditVehicle = async () => {
    const payload = {
      brand: selectedVehicle.brand.trim(),
      model: selectedVehicle.model.trim(),
      manufacture_year: selectedVehicle.manufacture_year,
      license_plate: selectedVehicle.license_plate.trim(),
      fuel_type: selectedVehicle.fuel_type.trim(),
      category_level_id: selectedVehicle.category_level_id,
    };

    try {
      const res = await fetch(`http://localhost:8000/api/vehicles/${selectedVehicle.id}`, {
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

      await fetchVehicles();
      setIsEditModalOpen(false);
      toast.success("Vehicle`s data changed")
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleAddClick = () => {
    setNewVehicle({
        brand: "",
        model: "",
        manufacture_year: 2010,
        license_plate: "",
        fuel_type: "",
        category_level_id: 0,
    });
    setIsAddModalOpen(true);
  };

  const handleAddVehicle = async () => {
    if (!newVehicle.category_level_id) {
        toast.error("Please select a category level.");
        return;
    }

    const payload = {
        brand: newVehicle.brand.trim(),
        model: newVehicle.model.trim(),
        manufacture_year: newVehicle.manufacture_year,
        license_plate: newVehicle.license_plate.trim(),
        fuel_type: newVehicle.fuel_type.trim(),
        category_level_id: newVehicle.category_level_id,
    };

    try {
      const res = await fetch("http://localhost:8000/api/vehicles/", {
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

      await fetchVehicles();
      setIsAddModalOpen(false)
      toast.success("Vehicle added")
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <>
      <Header />
      <div className="flex justify-center bg-gray-50 px-4 h-screen">
        <div className="w-full max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold text-center text-blue-800 mb-4">Vehicles List</h2>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Search</label>
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                    setPage(1); 
                    setSearchTerm(e.target.value);
                    }}
                    placeholder="e.g., Ford or Focus"
                    className="w-full border px-4 py-2 rounded"
                />
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Category Level (optional)</label>
                <Select
                  options={categoryOptions}
                  isClearable
                  onChange={(option) => setCategoryLevelId(option ? option.value : null)}
                  placeholder="Select category..."
                  styles={{
                    menu: base => ({ ...base, maxHeight: 200, overflowY: 'auto', zIndex: 11 }),
                  }}
                />
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Page size</label>
                <select
                    value={pageSize}
                    onChange={(e) => {
                    setPage(1);
                    setPageSize(parseInt(e.target.value));
                    }}
                    className="w-full border px-4 py-2 rounded"
                >
                    {[10, 25, 50, 100].map((size) => (
                    <option key={size} value={size}>
                        {size}
                    </option>
                    ))}
                </select>
              </div>

              <div>
                <button
                    onClick={() => handleAddClick(true)}
                    className="px-5 py-3 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                    Add vehicle
                </button>
              </div>

            </div>
          </div>

            <div className="max-h-[400px] overflow-y-auto overflow-x-auto rounded-lg shadow-lg border border-gray-200 bg-white">
              <table className="min-w-full bg-gray-50 rounded-md shadow border">
                <thead className="bg-blue-600 text-white sticky top-0 z-10">
                  <tr>
                    <th className="px-4 py-3 text-left">Brand</th>
                    <th className="px-4 py-3 text-left">Model</th>
                    <th className="px-4 py-3 text-left">Year</th>
                    <th className="px-4 py-3 text-left">License plate</th>
                    <th className="px-4 py-3 text-left">Fuel</th>
                    <th className="px-4 py-3 text-left">Category level</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {vehicles.map((vec, idx) => (
                    <tr key={vec.id} className={idx % 2 === 0 ? "bg-white" : "bg-gray-100"}>
                      <td className="px-4 py-3">{vec.brand}</td>
                      <td className="px-4 py-3">{vec.model}</td>
                      <td className="px-4 py-3">{vec.manufacture_year}</td>
                      <td className="px-4 py-3">{vec.license_plate}</td>
                      <td className="px-4 py-3">{vec.fuel_type}</td>
                      <td className="px-4 py-3">
                        {categoryOptions.find((opt) => opt.value === vec.category_level_id)?.label || "—"}
                      </td>
                      <td className="px-4 py-3">
                        <button
                            onClick={() => handleEditClick(vec)}
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

            <div className="flex justify-center items-center space-x-4 mt-6">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
            >
              ← Previous
            </button>
            <span className="text-lg font-semibold">{page}</span>
            <button
                onClick={() => setPage((p) => p + 1)}
                disabled={vehicles.length < pageSize}
                className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
                >
                Next →
            </button>
          </div>

          {loading && <p className="text-center mt-6">Loading vehicles...</p>}

          {isAddModalOpen  && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                  <h3 className="text-xl font-bold mb-4 text-blue-700">Add vehicle</h3>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Brand</label>
                      <input
                        type="text"
                        name="brand"
                        value={newVehicle.brand}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Model</label>
                      <input
                        type="text"
                        name="model"
                        value={newVehicle.model}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Year</label>
                      <input
                        type="number"
                        name="manufacture_year"
                        value={newVehicle.manufacture_year}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        min="1970"
                        max="3000"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">License plate</label>
                      <input
                        type="text"
                        name="license_plate"
                        value={newVehicle.license_plate}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Fuel</label>
                      <input
                        type="text"
                        name="fuel_type"
                        value={newVehicle.fuel_type}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                        <label className="block text-gray-700 font-semibold mb-2">Category Level</label>
                        <Select
                        options={categoryOptions}
                        value={categoryOptions.find((opt) => opt.value === newVehicle.category_level_id) || null}
                        onChange={(selected) =>
                        setNewVehicle((prev) => ({
                            ...prev,
                            category_level_id: selected ? selected.value : 0,
                        }))
                        }
                        placeholder="Select category level..."
                        styles={{
                            menu: base => ({ ...base, maxHeight: 200, overflowY: 'auto', zIndex: 11 }),
                        }}
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
                      onClick={handleAddVehicle}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Add
                    </button>
                  </div>
                </div>
            </div>
          )}

          {isEditModalOpen && selectedVehicle && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-700">Edit Vehicle</h3>

                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Brand</label>
                      <input
                        type="text"
                        name="brand"
                        value={selectedVehicle.brand}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Model</label>
                      <input
                        type="text"
                        name="model"
                        value={selectedVehicle.model}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Year</label>
                      <input
                        type="number"
                        name="manufacture_year"
                        value={selectedVehicle.manufacture_year}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        min="1970"
                        max="3000"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">License plate</label>
                      <input
                        type="text"
                        name="license_plate"
                        value={selectedVehicle.license_plate}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Fuel</label>
                      <input
                        type="text"
                        name="fuel_type"
                        value={selectedVehicle.fuel_type}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                        <label className="block text-gray-700 font-semibold mb-2">Category Level</label>
                        <Select
                        options={categoryOptions}
                        value={categoryOptions.find((opt) => opt.value === selectedVehicle.category_level_id) || null}
                        onChange={(selected) =>
                        setSelectedVehicle((prev) => ({
                            ...prev,
                            category_level_id: selected ? selected.value : 0,
                        }))
                        }
                        placeholder="Select category level..."
                        styles={{
                            menu: base => ({ ...base, maxHeight: 200, overflowY: 'auto', zIndex: 11 }),
                        }}
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
                      onClick={handleEditVehicle}
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

export default AdminVehicleList;
