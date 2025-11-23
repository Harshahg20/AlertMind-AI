import React from "react";
import OptimizedDashboard from "./OptimizedDashboard";
import AlertFeed from "../pages/AlertFeed";
import CascadeMap from "../pages/CascadeMap";
import AgentControl from "../pages/AgentControl";
import ClientCascadeView from "./ClientCascadeView";
import EnhancedPatchManagement from "./EnhancedPatchManagement";
import ITAdministrativeTasks from "./ITAdministrativeTasks";
// import OpsCenter from "./OpsCenter"; // Temporarily disabled

const TabContent = ({
  activeTab,
  alerts,
  predictions,
  clients,
  loading,
  stats,
  filteredData,
  onTabChange,
  remediationContext,
}) => {
  switch (activeTab) {
    case "dashboard":
      return (
        <OptimizedDashboard
          stats={stats}
          alerts={alerts}
          predictions={predictions}
          filteredData={filteredData}
          loading={loading}
        />
      );
    case "alerts":
      return (
        <AlertFeed
          alerts={alerts}
          filteredData={filteredData}
          loading={loading}
          onNavigate={onTabChange}
        />
      );
    case "cascade":
      return <ClientCascadeView clients={clients} loading={loading} />;
    case "ai":
      return <AgentControl />;
    case "patch":
      return <EnhancedPatchManagement clients={clients} loading={loading} remediationContext={remediationContext} />;
    case "admin":
      return <ITAdministrativeTasks clients={clients} loading={loading} />;
    // case "ops":
    //   return <OpsCenter clients={clients} loading={loading} />; // Temporarily disabled
    default:
      return null;
  }
};

export default TabContent;
