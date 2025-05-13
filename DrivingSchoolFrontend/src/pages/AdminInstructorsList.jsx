import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import Select from "react-select";
import { toast } from "react-toastify";
import CategoryModal from "../components/CategoryModal";

const AdminInstructorsList = () => {
  const [instructors, setInstructors] = useState([]);
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [categoryLevelId, setCategoryLevelId] = useState(null);
  const [sortBy, setSortBy] = useState("last_name");
  const [sortOrder, setSortOrder] = useState("asc");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [addInstructor, setAddInstructor] = useState({
    work_started_date: new Date().toISOString().split('T')[0],
    username: "",
    first_name: "",
    last_name: "",
    patronymic: "",
    birthday: "",
    phone_number: "",
    password: "",
  });
  const [isCategoriesModalOpen, setIsCategoriesModalOpen] = useState(false);
  const [selectedInstructor, setSelectedInstructor] = useState(null);

  const token = localStorage.getItem("access_token");

  useEffect(() => {
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
    fetchCategoryLevels();
  }, [token]);

  const fetchInstructors = async () => {
    setLoading(true);
    try {
      const url = new URL("http://localhost:8000/api/instructors/paginated");
      url.searchParams.append("page", page);
      url.searchParams.append("page_size", pageSize);
      url.searchParams.append("sort_by", sortBy);
      url.searchParams.append("sort_order", sortOrder);
      if (categoryLevelId) url.searchParams.append("category_level_id", categoryLevelId);
      if (searchTerm) url.searchParams.append("search", searchTerm);

      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setInstructors(data);
    } catch (err) {
      toast.error(err.message)
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInstructors();
  }, [page, sortBy, sortOrder, categoryLevelId, pageSize, searchTerm]);

  const handleEditClick = (instructor) => {
    setSelectedInstructor({
      ...instructor,
      ...instructor.user,
    });
    setIsEditModalOpen(true);
  };

  const handleAddClick = () => {
    setAddInstructor({
        work_started_date: new Date().toISOString().split('T')[0],
        username: "",
        first_name: "",
        last_name: "",
        patronymic: "",
        birthday: "",
        phone_number: "",
        password: "",
    });
    setIsAddModalOpen(true);
  };

  const handleCategoriesClick = (instructor) => {
    setSelectedInstructor({
      ...instructor,
      ...instructor.user,
    });
    setIsCategoriesModalOpen(true);
  };

  return (
    <>
      <Header />
      <div className="flex justify-center bg-gray-50 px-4 min-h-screen">
        <div className="w-full max-w-6xl mx-auto p-6">
          <h2 className="text-3xl font-bold text-center text-blue-800 mb-8">Instructors List</h2>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4 items-center">

              <div>
                <label className="block text-gray-700 font-semibold mb-2">Search</label>
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                    setPage(1); 
                    setSearchTerm(e.target.value);
                    }}
                    placeholder="e.g., Ivanov or ivan123"
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
                    onClick={() => handleAddClick()}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                    Add instructor
                </button>
              </div>

            </div>
          </div>

            <div className="max-h-[400px] overflow-y-auto overflow-x-auto rounded-lg shadow-lg border border-gray-200 bg-white">
              <table className="min-w-full bg-gray-50 rounded-md overflow-hidden shadow border">
                <thead className="bg-blue-600 text-white">
                  <tr>
                    <th className="px-4 py-3 text-left">Username</th>
                    <th className="px-4 py-3 text-left">Full Name</th>
                    <th className="px-4 py-3 text-left">Phone number</th>
                    <th className="px-4 py-3 text-left">Birthday</th>
                    <th className="px-4 py-3 text-left">Work started</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {instructors.map((inst, idx) => (
                    <tr key={inst.id} className={idx % 2 === 0 ? "bg-white" : "bg-gray-100"}>
                      <td className="px-4 py-3">{inst.user.username}</td>
                      <td className="px-4 py-3">
                        {inst.user.last_name} {inst.user.first_name} {inst.user.patronymic}
                      </td>
                      <td className="px-4 py-3">{inst.user.phone_number}</td>
                      <td className="px-4 py-3">{inst.user.birthday}</td>
                      <td className="px-4 py-3">{inst.work_started_date}</td>
                      <td className="px-4 py-3">
                        <button
                            onClick={() => handleEditClick(inst)}
                            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                        >
                            Edit
                        </button>
                        <button
                            onClick={() => handleCategoriesClick(inst)}
                            className="ml-3 px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                            >
                            Categories
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
                disabled={instructors.length < pageSize}
                className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
                >
                Next →
            </button>
          </div>

          {loading && <p className="text-center mt-6">Loading instructors...</p>}

          {isCategoriesModalOpen && selectedInstructor && (
            <CategoryModal instructorId={selectedInstructor.id} onClose={() => setIsCategoriesModalOpen(false)} />
          )}

          {isAddModalOpen && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-700">Add instructor</h3>
                <form
                    onSubmit={async (e) => {
                    e.preventDefault();

                    try {
                        const res = await fetch(`http://localhost:8000/api/instructors`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${token}`,
                        },
                        body: JSON.stringify({
                            work_started_date: addInstructor.work_started_date,
                            user: {
                            username: addInstructor.username.trim(),
                            first_name: addInstructor.first_name.trim(),
                            last_name: addInstructor.last_name.trim(),
                            patronymic: addInstructor.patronymic.trim() === "" ? null : addInstructor.patronymic.trim(),
                            birthday: addInstructor.birthday,
                            phone_number: addInstructor.phone_number.trim(),
                            },
                            password: addInstructor.password.trim(),
                        }),
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

                        await fetchInstructors();
                        setIsAddModalOpen(false);
                        toast.success("Instructor added")
                    } catch (err) {
                        toast.error(err.message)
                    }
                    }}
                >
                    {["work_started_date", "username", "first_name", "last_name", "patronymic", "birthday", "phone_number", "password"].map((field) => (
                    <div key={field} className="mb-3">
                        <label className="block text-gray-700 font-semibold mb-1">
                        {field.split("_").map(w => w[0].toUpperCase() + w.slice(1)).join(" ")}
                        </label>
                        <input
                        type={field === "birthday" ? "date" : field === "work_started_date" ? "date" : field === "password" ? "password" : "text"}
                        value={addInstructor[field] || ""}
                        onChange={(e) =>
                        setAddInstructor((prev) => ({
                            ...prev,
                            [field]: e.target.value,
                        }))
                        }
                          
                        className="w-full border px-4 py-2 rounded"
                        />
                    </div>
                    ))}

                    <div className="flex justify-end gap-2 mt-4">
                    <button
                        type="button"
                        onClick={() => setIsAddModalOpen(false)}
                        className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Add
                    </button>
                    </div>
                </form>
                </div>
            </div>
            )}

          {isEditModalOpen && selectedInstructor && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800/60 z-50">
                <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-lg">
                <h3 className="text-xl font-bold mb-4 text-blue-700">Edit instructor</h3>
                <form
                    onSubmit={async (e) => {
                    e.preventDefault();

                    try {
                        const res = await fetch(`http://localhost:8000/api/instructors/${selectedInstructor.id}`, {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${token}`,
                        },
                        body: JSON.stringify({
                            work_started_date: selectedInstructor.work_started_date,
                            user: {
                            username: selectedInstructor.username,
                            first_name: selectedInstructor.first_name.trim(),
                            last_name: selectedInstructor.last_name.trim(),
                            patronymic: selectedInstructor.patronymic.trim() === "" ? null : selectedInstructor.patronymic.trim(),
                            birthday: selectedInstructor.birthday,
                            phone_number: selectedInstructor.phone_number.trim(),
                            },
                            password: null,
                        }),
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

                        await fetchInstructors();
                        setIsEditModalOpen(false);
                        toast.success("Instructor`s data changed")
                    } catch (err) {
                        toast.error(err.message)
                    }
                    }}
                >
                    {["first_name", "last_name", "patronymic", "birthday", "phone_number"].map((field) => (
                    <div key={field} className="mb-3">
                        <label className="block text-gray-700 font-semibold mb-1">
                        {field.split("_").map(w => w[0].toUpperCase() + w.slice(1)).join(" ")}
                        </label>
                        <input
                        type={field === "birthday" ? "date" : "text"}
                        value={selectedInstructor[field] || ""}
                        onChange={(e) =>
                        setSelectedInstructor((prev) => ({
                            ...prev,
                            [field]: e.target.value,
                        }))
                        }
                          
                        className="w-full border px-4 py-2 rounded"
                        />
                    </div>
                    ))}

                    <div className="flex justify-end gap-2 mt-4">
                    <button
                        type="button"
                        onClick={() => setIsEditModalOpen(false)}
                        className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Save
                    </button>
                    </div>
                </form>
                </div>
            </div>
            )}

        </div>
      </div>
    </>
  );
};

export default AdminInstructorsList;
