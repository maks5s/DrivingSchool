import React, { useEffect, useState } from 'react';
import { PieChart } from '@mui/x-charts/PieChart';
import { toast } from 'react-toastify';
import Header from '../components/Header';

const StatisticCard = ({ title, count }) => (
  <div className="bg-white shadow-md rounded-2xl p-4 flex flex-col items-center justify-center border">
    <div className="text-2xl font-bold text-blue-600">{count}</div>
    <div className="text-gray-600 text-sm text-center mt-1">{title}</div>
  </div>
);

const ChartCard = ({ title, children }) => (
  <div className="bg-white shadow-md rounded-2xl p-4 border">
    <h3 className="text-xl font-semibold mb-2 text-center text-gray-700">{title}</h3>
    {children}
  </div>
);

const formatPieData = (items) =>
    items
      .slice()
      .sort((a, b) => a.category_name.localeCompare(b.category_name))
      .map((item, index) => ({
        id: index,
        value: item.count,
        label: item.category_name,
}));

const AdminStatisticsPage = () => {
  const [stats, setStats] = useState(null);

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/statistics/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setStats(data);
      } catch (err) {
        toast.error('Failed to fetch statistics:' + err);
      }
    };

    fetchStats();
  }, [token]);

  if (!stats) return (
    <>
        <Header />
        <div className="p-6 text-center text-gray-500">Loading...</div>
    </>
  );

  const {
    instructors_count,
    students_count,
    groups_count,
    vehicles_count,
    cabinets_count,
    category_levels_count,
    students_per_category,
    groups_per_category,
  } = stats;

  return (
    <>
        <Header />
        <div className="flex justify-center bg-gray-50 px-4 h-screen">
            <div className="w-full max-w-7xl mx-auto p-6">
                <h2 className="text-3xl font-bold text-center text-blue-800 mb-4">Statistics</h2>

                {stats ? (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 my-8">
                    <StatisticCard title="Instructors" count={instructors_count} />
                    <StatisticCard title="Students" count={students_count} />
                    <StatisticCard title="Groups" count={groups_count} />
                    <StatisticCard title="Vehicles" count={vehicles_count} />
                    <StatisticCard title="Cabinets" count={cabinets_count} />
                    <StatisticCard title="Category levels" count={category_levels_count} />
                  </div>
            
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <ChartCard title="Students by category levels">
                      <PieChart
                        series={[{
                          data: formatPieData(students_per_category),
                          highlightScope: { fade: 'global', highlight: 'item' },
                          faded: { innerRadius: 30, additionalRadius: -30, color: 'gray' },
                        }]}
                        height={250}
                      />
                    </ChartCard>
            
                    <ChartCard title="Groups by category levels">
                      <PieChart
                        series={[{
                          data: formatPieData(groups_per_category),
                          highlightScope: { fade: 'global', highlight: 'item' },
                          faded: { innerRadius: 30, additionalRadius: -30, color: 'gray' },
                        }]}
                        height={250}
                      />
                    </ChartCard>
                  </div>
                </>
                )
                : (<div className="p-6 text-center text-gray-500">Loading...</div>)}

            </div>
        </div>
    </>
  );
};

export default AdminStatisticsPage;
