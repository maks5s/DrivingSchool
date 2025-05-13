import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import { toast } from "react-toastify";
import Select from "react-select";

const AdminStudentsList = () => {
  const [loading, setLoading] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
  const [students, setStudents] = useState([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [sortBy, setSortBy] = useState("last_name");
  const [sortOrder, setSortOrder] = useState("asc");
  const [newStudent, setNewStudent] = useState({
    username: "",
    first_name: "",
    last_name: "",
    patronymic: "",
    birthday: "",
    phone_number: "",
    password: "",
    category_level_id: 0,
    group_id: 0,
  });
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedSchedule, setSelectedSchedule] = useState({
    instructor_id: 0,
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
  const [instructorByCategoryOptions, setInstructorByCategoryOptions] = useState([]);
  const [groupOptions, setGroupOptions] = useState([]);
  const [groupByCategoryOptions, setGroupByCategoryOptions] = useState([]);

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
    if (selectedStudent && selectedStudent.category_level_id !== 0) {
        try {
            const res = await fetch(`http://localhost:8000/api/category_levels/${selectedStudent.category_level_id}/instructors`, {
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
            toast.error("Failed to fetch instructors by category");
        }
    } else {
        setInstructorByCategoryOptions([])
    }
  };

  const fetchGroupsByCategory = async () => {
    if (newStudent.category_level_id !== 0) {
        try {
            const res = await fetch(`http://localhost:8000/api/category_levels/${newStudent.category_level_id}/groups`, {
            headers: { Authorization: `Bearer ${token}` },
            });
            const data = await res.json();
            setGroupByCategoryOptions(
            data.map((c) => ({
                value: c.id,
                label: c.name,
            }))
            );
        } catch (err) {
            toast.error("Failed to fetch groups by category");
        }
    } else {
        setGroupByCategoryOptions([])
    }
  };

  const fetchGroups = async () => {
    try {
        const res = await fetch("http://localhost:8000/api/groups/", {
        headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setGroupOptions(
        data.map((c) => ({
            value: c.id,
            label: c.name,
        }))
        );
    } catch (err) {
        toast.error("Failed to fetch groups");
    }
  };

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const url = new URL("http://localhost:8000/api/students/paginated");
      url.searchParams.append("page", page);
      url.searchParams.append("page_size", pageSize);
      url.searchParams.append("sort_by", sortBy);
      url.searchParams.append("sort_order", sortOrder);
      if (categoryLevelId) url.searchParams.append("category_level_id", categoryLevelId);
      if (searchTerm) url.searchParams.append("search", searchTerm);
      if (withoutSchedule) url.searchParams.append("only_without_sch", withoutSchedule);
    
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setStudents(data);
    } catch (error) {
      toast.error("Error fetching students:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategoryLevels();
    fetchGroups();
    fetchStudents();
  }, [token]);

  useEffect(() => {
    fetchInstructorsByCategory();
    fetchGroupsByCategory();
  }, [newStudent]);

  useEffect(() => {
    fetchInstructorsByCategory();
  }, [selectedStudent]);

  useEffect(() => {
    fetchStudents();
  }, [page, sortBy, sortOrder, categoryLevelId, pageSize, searchTerm, withoutSchedule]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewStudent((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditInputChange = (e) => {
    const { name, value } = e.target;
    setSelectedStudent((prev) => ({
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

  const handleEditClick = (student) => {
    setSelectedStudent({
      ...student,
      ...student.user,
    });
    setIsEditModalOpen(true);
  };

  const handleGenerateClick = (student) => {
    setSelectedStudent({ 
      ...student,
    });
    setSelectedSchedule({
        instructor_id: 0,
        start_date: new Date(Date.now() + 86400000).toISOString().slice(0, 10),
        end_date: new Date(Date.now() + 86400000 * 31).toISOString().slice(0, 10),
        schedules_per_day: 1,
        include_weekends: false,
    })
    setIsScheduleModalOpen(true);
  };

  const handleEditStudent = async () => {
    const payload = {
        user: {
            username: selectedStudent.username.trim(),
            first_name: selectedStudent.first_name.trim(),
            last_name: selectedStudent.last_name.trim(),
            patronymic: selectedStudent.patronymic.trim() === "" ? null : selectedStudent.patronymic.trim(),
            birthday: selectedStudent.birthday,
            phone_number: selectedStudent.phone_number.trim(),
        },
        password: null,
        category_level_id: selectedStudent.category_level_id,
        group_id: selectedStudent.group_id,
    };

    try {
      const res = await fetch(`http://localhost:8000/api/students/${selectedStudent.id}`, {
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

      await fetchStudents();
      setIsEditModalOpen(false);
      toast.success("Student`s data changed")
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleGenerateSchedule = async () => {
    if (!selectedSchedule.instructor_id) {
        toast.error("Please select an instructor");
        return;
    }

    const payload = {
      student_id: selectedStudent.id,
      instructor_id: selectedSchedule.instructor_id,
      start_date: selectedSchedule.start_date,
      end_date: selectedSchedule.end_date,
      schedules_per_day: selectedSchedule.schedules_per_day,
      include_weekends: selectedSchedule.include_weekends,
    };

    try {
      const res = await fetch(`http://localhost:8000/api/practice_schedules/create_butch`, {
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

      await fetchStudents();
      setIsScheduleModalOpen(false);
      toast.success(data.detail)
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleAddClick = () => {
    setNewStudent({
        username: "",
        first_name: "",
        last_name: "",
        patronymic: "",
        birthday: "",
        phone_number: "",
        password: "",
        category_level_id: 0,
        group_id: 0,
    });
    setIsAddModalOpen(true);
  };

  const handleAddStudent = async () => {
    if (!newStudent.category_level_id) {
        toast.error("Please select a category level");
        return;
    }
    if (!newStudent.group_id) {
        toast.error("Please select a group");
        return;
    }

    const payload = {
        user: {
            username: newStudent.username.trim(),
            first_name: newStudent.first_name.trim(),
            last_name: newStudent.last_name.trim(),
            patronymic: newStudent.patronymic.trim() === "" ? null : newStudent.patronymic.trim(),
            birthday: newStudent.birthday,
            phone_number: newStudent.phone_number.trim(),
        },
        password: newStudent.password.trim(),
        category_level_id: newStudent.category_level_id,
        group_id: newStudent.group_id,
    };

    try {
      const res = await fetch("http://localhost:8000/api/students/", {
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

      await fetchStudents();
      setIsAddModalOpen(false)
      toast.success("Student added")
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <>
      <Header />
      <div className="flex justify-center bg-gray-50 px-4 h-screen">
        <div className="w-full max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold text-center text-blue-800 mb-4">Students List</h2>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Search</label>
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                    setPage(1); 
                    setSearchTerm(e.target.value);
                    }}
                    placeholder="e.g., Ivanov or Ivan"
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
                <label className="block text-gray-700 font-semibold mb-2">Sort by</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full border px-4 py-2 rounded"
                >
                  <option value="last_name">Last Name</option>
                  <option value="first_name">First Name</option>
                  <option value="username">Username</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Order</label>
                <select
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value)}
                  className="w-full border px-4 py-2 rounded"
                >
                  <option value="asc">Ascending</option>
                  <option value="desc">Descending</option>
                </select>
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
                    Add student
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
                    <th className="px-4 py-3 text-left">Username</th>
                    <th className="px-4 py-3 text-left">Full Name</th>
                    <th className="px-4 py-3 text-left">Phone number</th>
                    <th className="px-4 py-3 text-left">Birthday</th>
                    <th className="px-4 py-3 text-left">Cat. level</th>
                    <th className="px-4 py-3 text-left">Group</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student, idx) => (
                    <tr key={student.id} className={idx % 2 === 0 ? "bg-white" : "bg-gray-100"}>
                      <td className="px-4 py-3">{student.user.username}</td>
                      <td className="px-4 py-3">
                        {student.user.last_name} {student.user.first_name} {student.user.patronymic}
                      </td>
                      <td className="px-4 py-3">{student.user.phone_number}</td>
                      <td className="px-4 py-3">{student.user.birthday}</td>
                      <td className="px-4 py-3">
                        {categoryOptions.find((opt) => opt.value === student.category_level_id)?.label || "—"}
                      </td>
                      <td className="px-4 py-3">
                        {groupOptions.find((opt) => opt.value === student.group_id)?.label || "—"}
                      </td>
                      <td className="px-4 py-3">
                        <button
                            onClick={() => handleEditClick(student)}
                            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                        >
                            Edit
                        </button>
                        {!student.has_schedule && (
                        <button
                            onClick={() => handleGenerateClick(student)}
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
                disabled={students.length < pageSize}
                className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
                >
                Next →
            </button>
          </div>

          {loading && <p className="text-center mt-6">Loading students...</p>}

          {isAddModalOpen  && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                  <h3 className="text-xl font-bold mb-4 text-blue-700">Add student</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Username</label>
                        <input
                            type="text"
                            name="username"
                            value={newStudent.username}
                            onChange={handleInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">First name</label>
                        <input
                            type="text"
                            name="first_name"
                            value={newStudent.first_name}
                            onChange={handleInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Last name</label>
                        <input
                            type="text"
                            name="last_name"
                            value={newStudent.last_name}
                            onChange={handleInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Patronymic</label>
                        <input
                            type="text"
                            name="patronymic"
                            value={newStudent.patronymic}
                            onChange={handleInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Birthday</label>
                        <input
                            type="date"
                            name="birthday"
                            value={newStudent.birthday}
                            onChange={handleInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Phone number</label>
                        <input
                            type="text"
                            name="phone_number"
                            value={newStudent.phone_number}
                            onChange={handleInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Password</label>
                        <input
                            type="password"
                            name="password"
                            value={newStudent.password}
                            onChange={handleInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block text-gray-700 font-semibold mb-2">Category Level</label>
                        <Select
                        options={categoryOptions}
                        value={categoryOptions.find((opt) => opt.value === newStudent.category_level_id) || null}
                        onChange={(selected) =>
                        setNewStudent((prev) => ({
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
                        <label className="block text-gray-700 font-semibold mb-2">Group</label>
                        <Select
                        options={groupByCategoryOptions}
                        value={groupByCategoryOptions.find((opt) => opt.value === newStudent.group_id) || null}
                        onChange={(selected) =>
                        setNewStudent((prev) => ({
                            ...prev,
                            group_id: selected ? selected.value : 0,
                        }))
                        }
                        placeholder="Select group..."
                        styles={{
                            menu: base => ({ ...base, maxHeight: 200, overflowY: 'auto', zIndex: 11 }),
                        }}
                        />
                    </div>
                  
                  </div>

                  <div className="flex justify-end gap-3 mt-6">
                    <button
                      onClick={() => setIsAddModalOpen(false)}
                      className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleAddStudent}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Add
                    </button>
                  </div>
                </div>
            </div>
          )}

          {isEditModalOpen && selectedStudent && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-700">Edit student</h3>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">First name</label>
                        <input
                            type="text"
                            name="first_name"
                            value={selectedStudent.first_name}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Last name</label>
                        <input
                            type="text"
                            name="last_name"
                            value={selectedStudent.last_name}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Patronymic</label>
                        <input
                            type="text"
                            name="patronymic"
                            value={selectedStudent.patronymic}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Birthday</label>
                        <input
                            type="date"
                            name="birthday"
                            value={selectedStudent.birthday}
                            onChange={handleEditInputChange}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                        />
                    </div>

                    <div>
                        <label className="block font-semibold text-gray-700 mb-1">Phone number</label>
                        <input
                            type="text"
                            name="phone_number"
                            value={selectedStudent.phone_number}
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
                      onClick={handleEditStudent}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Save
                    </button>
                  </div>

                </div>
            </div>
            )}

            {isScheduleModalOpen && selectedStudent && (
                <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                    <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                    <h3 className="text-xl font-bold mb-4 text-blue-700">Generate schedule for {selectedStudent.user.username}</h3>

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

                    <div>
                        <label className="block text-gray-700 font-semibold mb-2">Instructor</label>
                        <Select
                        options={instructorByCategoryOptions}
                        value={instructorByCategoryOptions.find((opt) => opt.value === selectedSchedule.instructor_id) || null}
                        onChange={(selected) =>
                        setSelectedSchedule((prev) => ({
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

export default AdminStudentsList;
