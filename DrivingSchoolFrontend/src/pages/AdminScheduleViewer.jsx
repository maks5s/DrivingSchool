import React, { useEffect, useState } from "react";
import Header from "../components/Header";
import Select from "react-select";
import { toast } from "react-toastify";

const AdminScheduleViewer = () => {
  const [students, setStudents] = useState([]);
  const [instructors, setInstructors] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedType, setSelectedType] = useState("student");
  const [selectedId, setSelectedId] = useState(null);
  const [schedule, setSchedule] = useState([]);
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [loading, setLoading] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const studentRes = await fetch("http://localhost:8000/api/students/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const instructorRes = await fetch("http://localhost:8000/api/instructors/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const groupRes = await fetch("http://localhost:8000/api/groups/", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!studentRes.ok) throw new Error("Failed to fetch students");
        else if (!instructorRes.ok) throw new Error("Failed to fetch instructors");
        else if (!groupRes.ok) throw new Error("Failed to fetch groups");

        const studentsData = await studentRes.json();
        const instructorsData = await instructorRes.json();
        const groupsData = await groupRes.json();

        setStudents(studentsData);
        setInstructors(instructorsData);
        setGroups(groupsData);
      } catch (err) {
        toast.error(err.message);
      }
    };

    fetchUsers();
  }, [token]);

  const fetchSchedule = async () => {
    if (!selectedId || !date) return;
    try {
      setLoading(true);
      const url = `http://localhost:8000/api/${selectedType}s/${selectedId}/schedule?dt=${date}`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to fetch schedule");
      const data = await res.json();
      setSchedule(data);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedId) {
      fetchSchedule();
    }
  }, [selectedId, date]);

  useEffect(() => {
    setSelectedId(null);
    setSelectedOption(null);
  }, [selectedType]);  

  return (
    <>
      <Header />
      <div className="flex justify-center h-screen bg-gray-50 px-4">
        <div className="w-full max-w-6xl mx-auto p-6">
            <h2 className="text-3xl font-bold text-center text-blue-800 mb-8">View Schedule</h2>

            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                <label className="block text-gray-700 font-semibold mb-2">Select type</label>
                <select
                    value={selectedType}
                    onChange={(e) => {
                    setSelectedType(e.target.value);
                    setSelectedId(null);
                    setSchedule([]);
                    }}
                    className="w-full border px-4 py-2 rounded"
                >
                    <option value="student">Student</option>
                    <option value="instructor">Instructor</option>
                    <option value="group">Group</option>
                </select>
                </div>

                <div>
                    <label className="block text-gray-700 font-semibold mb-2">Search by name</label>
                    <Select
                      options={(selectedType === "student" || selectedType === "instructor" ? (selectedType === "student" ? students : instructors) : groups).map((u) => ({
                        value: u.id,
                        label:
                          selectedType === "group"
                            ? u.name
                            : `${u.user.username} ${u.user.last_name} ${u.user.first_name} ${u.user.patronymic || ''}`,
                      }))}
                      value={selectedOption}
                      onChange={(option) => {
                        setSelectedOption(option);
                        setSelectedId(option ? option.value : null);
                      }}
                      placeholder="Start typing..."
                      isClearable
                      styles={{
                        menu: base => ({ ...base, maxHeight: 200, overflowY: 'auto', zIndex: 11 }),
                      }}
                    />
                </div>
            </div>
            </div>

            <div className="flex justify-center items-center gap-2 mt-4 mb-2 space-x-4">
                <button
                    onClick={() => setDate(prev => {
                    const newDate = new Date(prev);
                    newDate.setDate(newDate.getDate() - 1);
                    return newDate.toISOString().slice(0, 10);
                    })}
                    className="p-2 bg-blue-600 text-white rounded-md"
                >
                    ← Previous
                </button>
                <div>
                <label className="block text-gray-700 font-semibold mb-2">Select date</label>
                <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full border rounded"
                />
                </div>
                <button
                    onClick={() => setDate(prev => {
                    const newDate = new Date(prev);
                    newDate.setDate(newDate.getDate() + 1);
                    return newDate.toISOString().slice(0, 10);
                    })}
                    className="p-2 bg-blue-600 text-white rounded-md"
                >
                    Next →
                </button>
            </div>

            <div className="mt-8">
                {schedule.length === 0 && (<h3 className="text-xl font-bold mb-4 text-blue-700 text-center">No schedule found for {date}</h3>)} 
                {schedule.length !== 0 && 
                (<>
                    <h3 className="text-xl font-bold mb-4 text-blue-700 text-center">Schedule for {date}</h3>
                    <div className="max-h-[400px] overflow-y-auto overflow-x-auto rounded-lg shadow-lg border border-gray-200 max-h-[400px] overflow-y-auto bg-white">
                        <table className="min-w-full bg-gray-50 rounded-md overflow-hidden shadow border">
                            <thead className="bg-blue-600 text-white">
                            <tr>
                                <th className="px-4 py-3 text-left">Start Time</th>
                                <th className="px-4 py-3 text-left">End Time</th>
                                <th className="px-4 py-3 text-left">Type</th>
                                <th className="px-4 py-3 text-left">Extra</th>
                            </tr>
                            </thead>
                            <tbody>
                            {schedule.map((item, idx) => (
                                <tr
                                key={idx}
                                className={idx % 2 === 0 ? "bg-white" : "bg-gray-100"}
                                >
                                    <td className="px-4 py-3">
                                        {item.start_time}
                                    </td>
                                    <td className="px-4 py-3">
                                        {item.end_time}
                                    </td>
                                    <td className="px-4 py-3">{item.type}</td>
                                    <td className="px-4 py-3">{item.extra}</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>
                </>)}
            </div>

            {loading && <p className="text-center mt-6">Loading schedule...</p>}

        </div>
      </div>
    </>
  );
};

export default AdminScheduleViewer;
