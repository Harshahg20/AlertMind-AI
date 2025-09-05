import React, { useState } from "react";
import { Box, Toolbar } from "@mui/material";
import TopBar from "./TopBar";
import SideDrawer from "./SideDrawer";
import { drawerWidthExpanded, drawerWidthCollapsed } from "./constants";

const Layout = ({ stats, predictions, activeTab, onTabChange, children }) => {
  const [drawerOpen, setDrawerOpen] = useState(true);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        color: "text.primary",
      }}
    >
      <TopBar
        drawerOpen={drawerOpen}
        onToggleDrawer={() => setDrawerOpen((v) => !v)}
        stats={stats}
        predictions={predictions}
      />

      {/* Offset for fixed AppBar */}
      <Toolbar />

      <SideDrawer
        drawerOpen={drawerOpen}
        activeTab={activeTab}
        onChangeTab={onTabChange}
      />

      <Box
        component="main"
        sx={{
          px: { xs: 2, sm: 3, md: 4 },
          py: 3,
          ml: {
            lg: `${drawerOpen ? drawerWidthExpanded : drawerWidthCollapsed}px`,
          },
          transition: "margin 0.3s ease-in-out",
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
