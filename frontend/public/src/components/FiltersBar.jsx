import { Filter, Gift } from "lucide-react";

export default function FiltersBar({
  filters,
  setFilters,
  months,
  categories,
}) {
  return (
    <div className="bg-white border rounded-2xl p-4 shadow-sm">
      <div className="flex flex-col lg:flex-row gap-4 lg:items-end lg:justify-between">
        {/* Left Title */}
        <div>
          <div className="font-semibold flex items-center gap-2">
            <Filter size={18} />
            Filters
          </div>
          <div className="text-xs text-gray-500">
            Change month/category and simulate festival impact
          </div>
        </div>

        {/* Right Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full lg:w-auto">
          {/* Month */}
          <div>
            <label className="text-xs text-gray-500">Month</label>
            <select
              className="mt-1 w-full border rounded-xl px-3 py-2 text-sm bg-white"
              value={filters.month}
              onChange={(e) => setFilters((p) => ({ ...p, month: e.target.value }))}
            >
              {months.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          {/* Category */}
          <div>
            <label className="text-xs text-gray-500">Category</label>
            <select
              className="mt-1 w-full border rounded-xl px-3 py-2 text-sm bg-white"
              value={filters.category}
              onChange={(e) =>
                setFilters((p) => ({ ...p, category: e.target.value }))
              }
            >
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Festival Toggle */}
          <div>
            <label className="text-xs text-gray-500">Festival Mode</label>
            <button
              className={`mt-1 w-full border rounded-xl px-3 py-2 text-sm flex items-center justify-center gap-2
              ${filters.festival ? "bg-gray-900 text-white" : "bg-white"}`}
              onClick={() =>
                setFilters((p) => ({ ...p, festival: !p.festival }))
              }
            >
              <Gift size={16} />
              {filters.festival ? "ON (Simulating)" : "OFF"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
