import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { toast } from "react-toastify";
import Select from "react-select";

const AdminGroupsList = () => {
  const [loading, setLoading] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
  const [groups, setGroups] = useState([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newGroup, setNewGroup] = useState({
    name: "",
    created_date: new Date().toISOString().slice(0, 10),
    category_level_id: 0,
    instructor_id: 0,
  });
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [selectedSchedule, setSelectedSchedule] = useState({
    group_id: 0,
    start_date: new Date(Date.now() + 86400000).toISOString().slice(0, 10),
    end_date: new Date(Date.now() + 86400000 * 31).toISOString().slice(0, 10),
    schedules_per_day: 1,
    include_weekends: false,
  });
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryLevelId, setCategoryLevelId] = useState(null);
  const [pageSize, setPageSize] = useState(10);
  const [withoutSchedule, setWithoutSchedule] = useState(false);
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [instructorOptions, setInstructorOptions] = useState([]);
  const [instructorByCategoryOptions, setInstructorByCategoryOptions] = useState([]);

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

  const fetchInstructorsByCategory = async () => {
    if (newGroup.category_level_id !== 0) {
        try {
            const res = await fetch(`http://localhost:8000/api/category_levels/${newGroup.category_level_id}/instructors`, {
            headers: { Authorization: `Bearer ${token}` },
            });
            const data = await res.json();
            setInstructorByCategoryOptions(
            data.map((c) => ({
                value: c.id,
                label: `${c.user.last_name} ${c.user.first_name[0]}. ${c.user.patronymic ? c.user.patronymic[0] + '.' : ''}`,
            }))
            );
        } catch (err) {
            toast.error("Failed to fetch instructors by category" + err);
        }
    } else {
        setInstructorByCategoryOptions([])
    }
  };

  const fetchInstructors = async () => {
    try {
        const res = await fetch("http://localhost:8000/api/instructors/", {
        headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setInstructorOptions(
        data.map((c) => ({
            value: c.id,
            label: `${c.user.last_name} ${c.user.first_name[0]}. ${c.user.patronymic ? c.user.patronymic[0] + '.' : ''}`,
        }))
        );
    } catch (err) {
        toast.error("Failed to fetch instructors");
    }
  };

  const fetchGroups = async () => {
    setLoading(true);
    try {
      const url = new URL("http://localhost:8000/api/groups/paginated");
      url.searchParams.append("page", page);
      url.searchParams.append("page_size", pageSize);
      if (categoryLevelId) url.searchParams.append("category_level_id", categoryLevelId);
      if (searchTerm) url.searchParams.append("search", searchTerm);
      if (withoutSchedule) url.searchParams.append("only_without_sch", withoutSchedule);
    
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setGroups(data);
    } catch (error) {
      toast.error("Error fetching groups:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategoryLevels();
    fetchInstructors();
    fetchGroups();
  }, [token]);

  useEffect(() => {
    fetchInstructorsByCategory();
  }, [newGroup]);

  useEffect(() => {
    fetchGroups();
  }, [page, categoryLevelId, pageSize, searchTerm, withoutSchedule]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewGroup((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setSelectedGroup((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleGenerateInputChange = (e) => {
    const { name, value } = e.target;
    setSelectedSchedule((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditClick = (group) => {
    setSelectedGroup({
      ...group,
    });
    setIsEditModalOpen(true);
  };

  const handleGenerateClick = (group) => {
    setSelectedGroup({
      ...group,
    });
    setIsScheduleModalOpen(true);
  };

  const handleEditGroup = async () => {
    const payload = {
      name: selectedGroup.name.trim(),
      created_date: selectedGroup.created_date,
      category_level_id: selectedGroup.category_level_id,
      instructor_id: selectedGroup.instructor_id,
    };

    try {
      const res = await fetch(`http://localhost:8000/api/groups/${selectedGroup.id}`, {
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

      await fetchGroups();
      setIsEditModalOpen(false);
      toast.success("Group`s data changed")
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleGenerateSchedule = async () => {
    const payload = {
      group_id: selectedGroup.id,
      start_date: selectedSchedule.start_date,
      end_date: selectedSchedule.end_date,
      schedules_per_day: selectedSchedule.schedules_per_day,
      include_weekends: selectedSchedule.include_weekends,
    };

    try {
      const res = await fetch(`http://localhost:8000/api/group_schedules/create_butch`, {
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

      await fetchGroups();
      setIsScheduleModalOpen(false);
      toast.success(data.detail)
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleAddClick = () => {
    setNewGroup({
        name: "",
        created_date: new Date().toISOString().slice(0, 10),
        category_level_id: 0,
        instructor_id: 0,
    });
    setIsAddModalOpen(true);
  };

  const handleAddGroup = async () => {
    if (!newGroup.category_level_id) {
        toast.error("Please select a category level.");
        return;
    }
    if (!newGroup.instructor_id) {
        toast.error("Please select a instructor.");
        return;
    }

    const payload = {
        name: newGroup.name.trim(),
        created_date: newGroup.created_date,
        category_level_id: newGroup.category_level_id,
        instructor_id: newGroup.instructor_id,
    };

    try {
      const res = await fetch("http://localhost:8000/api/groups/", {
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

      await fetchGroups();
      setIsAddModalOpen(false)
      toast.success("Group added")
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <>
      <Header />
      <div className="flex justify-center bg-gray-50 px-4 h-screen">
        <div className="w-full max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold text-center text-blue-800 mb-4">Groups List</h2>

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
                    placeholder="e.g., Group 1"
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
                    Add group
                </button>
              </div>

              <div className="flex items-center">
                    <label className="block text-gray-700 font-semibold pr-4">Only without schedule</label>
                    <input
                        type="checkbox"
                        name="only_without_sch"
                        checked={withoutSchedule}
                        onChange={(e) => setWithoutSchedule(e.target.checked)}
                        className="w-4 h-4 text-blue-600 rounded-sm"
                    />
              </div>

            </div>
          </div>

            <div className="max-h-[400px] overflow-y-auto overflow-x-auto rounded-lg shadow-lg border border-gray-200 bg-white">
              <table className="min-w-full bg-gray-50 rounded-md shadow border">
                <thead className="bg-blue-600 text-white sticky top-0 z-10">
                  <tr>
                    <th className="px-4 py-3 text-left">Name</th>
                    <th className="px-4 py-3 text-left">Created date</th>
                    <th className="px-4 py-3 text-left">Category level</th>
                    <th className="px-4 py-3 text-left">Instructor</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {groups.map((group, idx) => (
                    <tr key={group.id} className={idx % 2 === 0 ? "bg-white" : "bg-gray-100"}>
                      <td className="px-4 py-3">{group.name}</td>
                      <td className="px-4 py-3">{group.created_date}</td>
                      <td className="px-4 py-3">
                        {categoryOptions.find((opt) => opt.value === group.category_level_id)?.label || "—"}
                      </td>
                      <td className="px-4 py-3">
                        {instructorOptions.find((opt) => opt.value === group.instructor_id)?.label || "—"}
                      </td>
                      <td className="px-4 py-3">
                        <button
                            onClick={() => handleEditClick(group)}
                            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                        >
                            Edit
                        </button>
                        {!group.has_schedule && (
                        <button
                            onClick={() => handleGenerateClick(group)}
                            className="ml-2 px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                        >
                            Generate schedule
                        </button>)}
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
                disabled={groups.length < pageSize}
                className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
                >
                Next →
            </button>
          </div>

          {loading && <p className="text-center mt-6">Loading groups...</p>}

          {isAddModalOpen  && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                  <h3 className="text-xl font-bold mb-4 text-blue-700">Add group</h3>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Name</label>
                      <input
                        type="text"
                        name="name"
                        value={newGroup.name}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Created date</label>
                      <input
                        type="date"
                        name="created_date"
                        value={newGroup.created_date}
                        onChange={handleInputChange}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                      />
                    </div>
                    <div>
                        <label className="block text-gray-700 font-semibold mb-2">Category Level</label>
                        <Select
                        options={categoryOptions}
                        value={categoryOptions.find((opt) => opt.value === newGroup.category_level_id) || null}
                        onChange={(selected) =>
                        setNewGroup((prev) => ({
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
                    <div>
                        <label className="block text-gray-700 font-semibold mb-2">Instructor</label>
                        <Select
                        options={instructorByCategoryOptions}
                        value={instructorByCategoryOptions.find((opt) => opt.value === newGroup.instructor_id) || null}
                        onChange={(selected) =>
                        setNewGroup((prev) => ({
                            ...prev,
                            instructor_id: selected ? selected.value : 0,
                        }))
                        }
                        placeholder="Select instructor..."
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
                      onClick={handleAddGroup}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Add
                    </button>
                  </div>
                </div>
            </div>
          )}

          {isEditModalOpen && selectedGroup && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-700">Edit group</h3>

                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Name</label>
                      <input
                        type="text"
                        name="name"
                        value={selectedGroup.name}
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
                      onClick={handleEditGroup}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Save
                    </button>
                  </div>

                </div>
            </div>
            )}

            {isScheduleModalOpen && selectedGroup && (
                <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                    <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                    <h3 className="text-xl font-bold mb-4 text-blue-700">Generate schedule for {selectedGroup.name}</h3>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Start date</label>
                        <input
                            type="date"
                            name="start_date"
                            value={selectedSchedule.start_date}
                            onChange={handleGenerateInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">End date</label>
                        <input
                            type="date"
                            name="end_date"
                            value={selectedSchedule.end_date}
                            onChange={handleGenerateInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Schedules per day</label>
                        <input
                            type="number"
                            name="schedules_per_day"
                            value={selectedSchedule.schedules_per_day}
                            onChange={handleGenerateInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            min="1"
                            max="20"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Include weekends</label>
                        <input
                            type="checkbox"
                            name="include_weekends"
                            value={selectedSchedule.include_weekends}
                            onChange={handleGenerateInputChange}
                            className="w-4 h-4 text-blue-600 rounded-sm"
                        />
                    </div>

                    <div className="flex justify-end gap-3 mt-6">
                        <button
                        onClick={() => setIsScheduleModalOpen(false)}
                        className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                        >
                        Cancel
                        </button>
                        <button
                        onClick={handleGenerateSchedule}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                        Generate
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

export default AdminGroupsList;
