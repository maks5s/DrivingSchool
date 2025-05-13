import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { toast } from "react-toastify";

const AdminCategoryLevelsList = () => {
  const [loading, setLoading] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [categoryLevels, setCategoryLevels] = useState([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newCategoryLevel, setNewCategoryLevel] = useState({
    category: "",
    transmission: "",
    description: "",
    theory_lessons_count: 20,
    practice_lessons_count: 20,
    theory_lessons_duration: "02:00:00",
    practice_lessons_duration: "02:00:00",
    minimum_age_to_get: 16,
  });
  const [selectedCategoryLevel, setSelectedCategoryLevel] = useState(null);

  const token = localStorage.getItem("access_token");

  const fetchCategoryLevels = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/category_levels/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setCategoryLevels(data);
    } catch (error) {
      toast.error("Error fetching category levels:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategoryLevels();
  }, [token]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCategoryLevel((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setSelectedCategoryLevel((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditClick = (level) => {
    setSelectedCategoryLevel({
      ...level,
      ...level.category_level_info,
    });
    setIsEditModalOpen(true);
  };

  const handleEditCategoryLevel = async () => {
    const payload = {
      category: selectedCategoryLevel.category.trim(),
      transmission: selectedCategoryLevel.transmission.trim(),
      description: selectedCategoryLevel.description.trim(),
      theory_lessons_count: selectedCategoryLevel.theory_lessons_count,
      practice_lessons_count: selectedCategoryLevel.practice_lessons_count,
      theory_lessons_duration: selectedCategoryLevel.theory_lessons_duration,
      practice_lessons_duration: selectedCategoryLevel.practice_lessons_duration,
      minimum_age_to_get: selectedCategoryLevel.minimum_age_to_get,
    };

    try {
      const res = await fetch(`http://localhost:8000/api/category_levels/${selectedCategoryLevel.id}`, {
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

      await fetchCategoryLevels();
      setIsEditModalOpen(false);
      toast.success("Category level`s data changed")
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleAddClick = () => {
    setNewCategoryLevel({
      category: "",
      transmission: "",
      description: "",
      theory_lessons_count: 20,
      practice_lessons_count: 20,
      theory_lessons_duration: "02:00:00",
      practice_lessons_duration: "02:00:00",
      minimum_age_to_get: 16,
    });
    setIsAddModalOpen(true);
  };

  const handleAddCategoryLevel = async () => {
    const payload = {
      category: newCategoryLevel.category.trim(),
      transmission: newCategoryLevel.transmission.trim(),
      description: newCategoryLevel.description.trim(),
      theory_lessons_count: newCategoryLevel.theory_lessons_count,
      practice_lessons_count: newCategoryLevel.practice_lessons_count,
      theory_lessons_duration: newCategoryLevel.theory_lessons_duration,
      practice_lessons_duration: newCategoryLevel.practice_lessons_duration,
      minimum_age_to_get: newCategoryLevel.minimum_age_to_get,
    };

    try {
      const res = await fetch("http://localhost:8000/api/category_levels/", {
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

      await fetchCategoryLevels();
      setIsAddModalOpen(false)
      toast.success("Category level added")
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <>
      <Header />
      <div className="flex justify-center bg-gray-50 px-4 h-screen">
        <div className="w-full max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold text-center text-blue-800 mb-4">Category levels List</h2>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-1 gap-4 mb-4">

              <div className="flex justify-center">
                <button
                    onClick={() => handleAddClick(true)}
                    className="px-5 py-3 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                    Add category level
                </button>
              </div>

            </div>
          </div>

            <div className="max-h-[500px] overflow-y-auto overflow-x-auto rounded-lg shadow-lg border border-gray-200 bg-white">
              <table className="min-w-full bg-gray-50 rounded-md shadow border">
                <thead className="bg-blue-600 text-white sticky top-0 z-10">
                  <tr>
                    <th className="px-4 py-3 text-left">Category</th>
                    <th className="px-4 py-3 text-left">Transmission</th>
                    <th className="px-4 py-3 text-left">Theory</th>
                    <th className="px-4 py-3 text-left">Practice</th>
                    <th className="px-4 py-3 text-left">Minimal age</th>
                    <th className="px-4 py-3 text-left">Description</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {categoryLevels.map((level, idx) => (
                    <tr key={level.id} className={idx % 2 === 0 ? "bg-white" : "bg-gray-100"}>
                      <td className="px-4 py-3">{level.category}</td>
                      <td className="px-4 py-3">{level.transmission}</td>
                      <td className="px-4 py-3">
                        {level.category_level_info.theory_lessons_count} : {level.category_level_info.theory_lessons_duration}
                      </td>
                      <td className="px-4 py-3">
                        {level.category_level_info.practice_lessons_count} : {level.category_level_info.practice_lessons_duration}
                      </td>
                      <td className="px-4 py-3">{level.category_level_info.minimum_age_to_get}</td>
                      <td className="px-4 py-3 break-words whitespace-pre-wrap max-w-xs">{level.description}</td>
                      <td className="px-4 py-3">
                        <button
                            onClick={() => handleEditClick(level)}
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

          {loading && <p className="text-center mt-6">Loading category levels...</p>}

          {isAddModalOpen  && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                  <h3 className="text-xl font-bold mb-4 text-blue-700">Add category level</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Category</label>
                      <input
                        type="text"
                        name="category"
                        value={newCategoryLevel.category}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Transmission</label>
                      <input
                        type="text"
                        name="transmission"
                        value={newCategoryLevel.transmission}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Theory lessons count</label>
                      <input
                        type="number"
                        name="theory_lessons_count"
                        value={newCategoryLevel.theory_lessons_count}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        min="1"
                        max="100"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Practice lessons count</label>
                      <input
                        type="number"
                        name="practice_lessons_count"
                        value={newCategoryLevel.practice_lessons_count}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        min="1"
                        max="100"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Theory duration</label>
                      <input
                        type="time"
                        name="theory_lessons_duration"
                        value={newCategoryLevel.theory_lessons_duration}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        step="1"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Practice duration</label>
                      <input
                        type="time"
                        name="practice_lessons_duration"
                        value={newCategoryLevel.practice_lessons_duration}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        step="1"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Minimal age</label>
                      <input
                        type="number"
                        name="minimum_age_to_get"
                        value={newCategoryLevel.minimum_age_to_get}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        min="16"
                        max="100"
                      />
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block font-semibold text-gray-700 mb-1">Description</label>
                    <textarea
                      name="description"
                      value={newCategoryLevel.description}
                      onChange={handleInputChange}
                      rows={4}
                      className="w-full border border-gray-300 rounded px-3 py-2 resize-y"
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
                      onClick={handleAddCategoryLevel}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Add
                    </button>
                  </div>
                </div>
            </div>
          )}

          {isEditModalOpen && selectedCategoryLevel && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-700">Edit Category level</h3>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Category</label>
                      <input
                        type="text"
                        name="category"
                        value={selectedCategoryLevel.category}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Transmission</label>
                      <input
                        type="text"
                        name="transmission"
                        value={selectedCategoryLevel.transmission}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Theory lessons count</label>
                      <input
                        type="number"
                        name="theory_lessons_count"
                        value={selectedCategoryLevel.theory_lessons_count}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        min="1"
                        max="100"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Practice lessons count</label>
                      <input
                        type="number"
                        name="practice_lessons_count"
                        value={selectedCategoryLevel.practice_lessons_count}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        min="1"
                        max="100"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Theory duration</label>
                      <input
                        type="time"
                        name="theory_lessons_duration"
                        value={selectedCategoryLevel.theory_lessons_duration}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        step="1"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Practice duration</label>
                      <input
                        type="time"
                        name="practice_lessons_duration"
                        value={selectedCategoryLevel.practice_lessons_duration}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        step="1"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Minimal age</label>
                      <input
                        type="number"
                        name="minimum_age_to_get"
                        value={selectedCategoryLevel.minimum_age_to_get}
                        onChange={handleEditInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        min="16"
                        max="100"
                      />
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block font-semibold text-gray-700 mb-1">Description</label>
                    <textarea
                      name="description"
                      value={selectedCategoryLevel.description}
                      onChange={handleEditInputChange}
                      rows={4}
                      className="w-full border border-gray-300 rounded px-3 py-2 resize-y"
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
                      onClick={handleEditCategoryLevel}
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

export default AdminCategoryLevelsList;
