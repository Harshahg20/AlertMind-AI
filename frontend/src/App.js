import React from "react";
import "./App.css";
import { Box, Typography, useTheme } from "@mui/material";
import Layout from "./layout/Layout";
import TabContent from "./components/TabContent";
import { useAppData } from "./hooks/useAppData";

function App() {
  const theme = useTheme();
  const {
    activeTab,
    alerts,
    predictions,
    clients,
    loading,
    stats,
    filteredData,
    handleTabChange,
  } = useAppData();

  if (loading && alerts.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-white">Loading CascadeGuard AI...</p>
        </div>
      </div>
    );
  }

  return (
    <Layout
      stats={stats}
      predictions={predictions}
      activeTab={activeTab}
      onTabChange={handleTabChange}
    >
      <TabContent
        activeTab={activeTab}
        alerts={alerts}
        predictions={predictions}
        clients={clients}
        loading={loading}
        stats={stats}
        filteredData={filteredData}
      />
      <Box
        component="footer"
        sx={{
          borderTop: `1px solid ${theme.palette.primary.main}22`,
          py: 2,
          textAlign: "center",
        }}
      >
        <Typography variant="caption" color="text.secondary">
          CascadeGuard AI Demo • Data refreshes every 30 seconds
        </Typography>
      </Box>
    </Layout>
  );
}

export default App;
