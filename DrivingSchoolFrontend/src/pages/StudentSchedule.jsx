import React, { useEffect, useState } from "react";
import { jwtDecode } from "jwt-decode";
import Header from "../components/Header";
import { toast } from "react-toastify";

const StudentSchedule = () => {
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);

  const fetchSchedule = async (date) => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      if (!token) throw new Error("No access token found");

      const decoded = jwtDecode(token);
      const studentId = decoded.sub;

      const response = await fetch(
        `http://localhost:8000/api/students/${studentId}/schedule?dt=${date}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch schedule");
      }

      const data = await response.json();
      setSchedule(data);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedule(selectedDate);
  }, [selectedDate]);

  const handleDateChange = (direction) => {
    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() + direction);
    setSelectedDate(newDate.toISOString().split("T")[0]);
  };

  return (
    <>
    <Header />
    <div className="flex justify-center h-screen bg-gray-50 px-4">
      <div className="w-full max-w-6xl mt-6">
        <h2 className="text-3xl font-bold mb-6 text-center text-blue-800">
          My schedule
        </h2>

        <div className="mb-6 flex justify-center items-center space-x-4">
            <button
            onClick={() => handleDateChange(-1)}
            className="p-2 bg-blue-600 text-white rounded-md"
            >
            ← Previous
            </button>

            <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="p-2 border rounded-md"
            />

            <button
            onClick={() => handleDateChange(1)} 
            className="p-2 bg-blue-600 text-white rounded-md"
            >
            Next →
            </button>
        </div>

        {schedule.length === 0 && (<h3 className="text-xl font-bold mb-4 text-blue-700 text-center">No schedule found for {selectedDate}</h3>)}
        {schedule.length !== 0 && (
            <div className="overflow-x-auto rounded-lg shadow-lg border border-gray-200 max-h-[700px] overflow-y-auto bg-white">
            <table className="min-w-full text-base text-gray-700">
                <thead className="bg-blue-600 text-white sticky top-0 z-10">
                    <tr>
                    <th className="px-6 py-4 text-left">Start time</th>
                    <th className="px-6 py-4 text-left">End time</th>
                    <th className="px-6 py-4 text-left">Schedule type</th>
                    <th className="px-6 py-4 text-left">Additional info</th>
                    </tr>
                </thead>
                <tbody>
                    {schedule.map((lesson, index) => (
                    <tr
                        key={index}
                        className={index % 2 === 0 ? "bg-gray-50" : "bg-white hover:bg-blue-50"}
                    >
                        <td className="px-6 py-4">{lesson.start_time}</td>
                        <td className="px-6 py-4">{lesson.end_time}</td>
                        <td className="px-6 py-4">{lesson.type}</td>
                        <td className="px-6 py-4">{lesson.extra}</td>
                    </tr>
                    ))}
                </tbody>
                </table>
            </div>)}
            
        {loading && <p className="text-center mt-8">Loading schedule...</p>}

      </div>
    </div>
    </>
  );
};

export default StudentSchedule;
