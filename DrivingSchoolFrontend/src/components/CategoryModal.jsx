import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";

const CategoryModal = ({ instructorId, onClose }) => {
    const [allCategories, setAllCategories] = useState([]);
    const [instructorCategories, setInstructorCategories] = useState([]);
    const token = localStorage.getItem("access_token");
  
    useEffect(() => {
      fetchAll();
    }, []);
  
    const fetchAll = async () => {
      try{
          const [allRes, instRes] = await Promise.all([
            fetch("http://localhost:8000/api/category_levels/", {
              headers: { Authorization: `Bearer ${token}` },
            }),
            fetch(`http://localhost:8000/api/instructors/${instructorId}/categories`, {
              headers: { Authorization: `Bearer ${token}` },
            }),
          ]);
      
          const all = await allRes.json();
          const inst = await instRes.json();
      
          setAllCategories(all);
          setInstructorCategories(inst.map((c) => c.id));
      }
      catch (err) {
        toast.error(err.message)
      }
    };
  
    const handleCheckboxChange = async (checked, categoryId) => {
      const url = checked
        ? `http://localhost:8000/api/instructors/${instructorId}/categories?category_level_id=${categoryId}`
        : `http://localhost:8000/api/instructors/${instructorId}/categories/${categoryId}`;
  
      const method = checked ? "POST" : "DELETE";
  
      try {
        const res = await fetch(url, {
        method,
        headers: { Authorization: `Bearer ${token}` },
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

        const updated = checked
            ? [...instructorCategories, categoryId]
            : instructorCategories.filter((id) => id !== categoryId);
        setInstructorCategories(updated);

        toast.success(data.detail)
      }
      catch (err) {
        toast.error(err.message)
      }
    };
  
    return (
      <div className="fixed inset-0 bg-gray-800/60 flex justify-center items-center">
        <div className="bg-white p-6 rounded-lg w-full max-w-md">
          <h3 className="text-xl font-bold mb-4 text-blue-700">Instructor`s category levels</h3>
          <div className="space-y-2 max-h-[400px] overflow-y-auto p-1">
            {allCategories.map((cat) => (
              <label key={cat.id} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  className="w-4 h-4 text-blue-600 rounded-sm"
                  checked={instructorCategories.includes(cat.id)}
                  onChange={(e) => handleCheckboxChange(e.target.checked, cat.id)}
                />
                <span className="font-semibold">{cat.category} {cat.transmission}</span>
              </label>
            ))}
          </div>
          <div className="mt-4 text-right">
            <button onClick={onClose} className="px-4 py-2 bg-blue-600 text-white rounded">
              Close
            </button>
          </div>
        </div>
      </div>
    );
  };

export default CategoryModal;