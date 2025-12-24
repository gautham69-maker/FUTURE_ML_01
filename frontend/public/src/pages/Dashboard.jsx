import { useEffect, useRef, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import KPICards from "../components/KPICards";
import SalesChart from "../components/SalesChart";
import CategoryChart from "../components/CategoryChart";
import FiltersBar from "../components/FiltersBar";
import { getDashboardData } from "../services/api";

export default function Dashboard() {
  const [data, setData] = useState(null);

  const [filters, setFilters] = useState({
    month: "All",
    category: "All",
    festival: false,
  });

  const months = [
    "All", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];
  const categories = ["All", "Food", "Clothes", "Electronics", "Utensils", "Books"];

  // ✅ StrictMode-safe guard (prevents effect from running twice in dev)
  const didInit = useRef(false);

  useEffect(() => {
    if (didInit.current) return;
    didInit.current = true;

    const d = getDashboardData();
    setData(d);
  }, []);

  if (!data) return <div className="p-6">Loading...</div>;

  const filteredMonthlySales =
    filters.month === "All"
      ? data.monthlySales
      : data.monthlySales.filter((x) => x.month === filters.month);

  const festivalMultiplier = filters.festival ? 1.15 : 1;

  const monthlySalesForChart = filteredMonthlySales.map((x) => ({
    ...x,
    sales: Math.round(x.sales * festivalMultiplier),
  }));

  const categorySalesForChart =
    filters.category === "All"
      ? data.categorySales
      : data.categorySales.filter((x) => x.category === filters.category);

  return (
    <div>
      <Navbar />

      <div className="flex">
        <Sidebar />

        <div className="flex-1 p-6 space-y-6">
          <KPICards kpis={data.kpis} />

          <FiltersBar
            filters={filters}
            setFilters={setFilters}
            months={months}
            categories={categories}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SalesChart data={monthlySalesForChart} />
            <CategoryChart data={categorySalesForChart} />
          </div>

          <div className="bg-white border rounded-2xl p-4 shadow-sm text-sm">
            <div className="font-semibold">Quick Insight</div>
            <div className="text-gray-600 mt-1">
              {filters.festival
                ? `Festival mode is ON → Sales boosted by ~15%. Consider discounts mainly for ${
                    filters.category === "All" ? "Electronics & Clothes" : filters.category
                  }.`
                : "Festival mode is OFF → Use this view to identify low-sales months and run targeted discounts."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
