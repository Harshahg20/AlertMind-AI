import React, { useState } from "react";
import EnhancedPatchManagement from "./EnhancedPatchManagement";
import ITAdministrativeTasks from "./ITAdministrativeTasks";

const OpsCenter = ({ clients = [], loading = false }) => {
  const [activeModule, setActiveModule] = useState("patch");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Operations Center</h2>
          <p className="text-gray-400 mt-1">
            Unified workspace for Patch Management and IT Administrative Tasks
          </p>
        </div>
        <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
          {[
            { id: "patch", label: "Patch Management" },
            { id: "admin", label: "IT Admin Tasks" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveModule(tab.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeModule === tab.id
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {activeModule === "patch" ? (
        <EnhancedPatchManagement clients={clients} loading={loading} />)
        : (
        <ITAdministrativeTasks clients={clients} loading={loading} />
      )}
    </div>
  );
};

export default OpsCenter;
