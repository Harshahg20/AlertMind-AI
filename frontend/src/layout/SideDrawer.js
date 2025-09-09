import React from "react";
import {
  Drawer,
  Toolbar,
  Divider,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Stack,
  Avatar,
  Typography,
  Box,
  useTheme,
} from "@mui/material";
import InsightsIcon from "@mui/icons-material/Insights";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import LanIcon from "@mui/icons-material/Lan";
import { drawerWidthExpanded, drawerWidthCollapsed } from "./constants";

const navItems = [
  { id: "ops", label: "Ops Console", icon: <InsightsIcon /> },
  { id: "alerts", label: "Alert Feed", icon: <WarningAmberIcon /> },
  { id: "cascade", label: "Cascade Map", icon: <LanIcon /> },
  { id: "agent", label: "AI Agent", icon: <SmartToyIcon /> },
];

const SideDrawer = ({ drawerOpen, activeTab, onChangeTab }) => {
  const theme = useTheme();
  return (
    <Drawer
      variant="permanent"
      open={drawerOpen}
      sx={{
        width: drawerOpen ? drawerWidthExpanded : drawerWidthCollapsed,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: drawerOpen ? drawerWidthExpanded : drawerWidthCollapsed,
          boxSizing: "border-box",
          borderRight: `1px solid ${theme.palette.primary.main}33`,
          background: `radial-gradient(1200px 800px at -100px -200px, rgba(33,150,243,0.18) 0%, rgba(33,150,243,0.05) 30%, rgba(255,255,255,0.02) 100%)`,
          backdropFilter: "blur(14px) saturate(120%)",
          WebkitBackdropFilter: "blur(14px) saturate(120%)",
          transition: "width 0.3s ease-in-out",
        },
      }}
    >
      <Toolbar sx={{ minHeight: 56 }} />
      <Divider />
      {drawerOpen && (
        <>
          <Stack
            direction="row"
            spacing={1.5}
            alignItems="center"
            sx={{ px: 2, py: 2 }}
          >
            <Avatar
              sx={{
                bgcolor: "primary.dark",
                backgroundImage: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                width: 36,
                height: 36,
                fontWeight: 800,
              }}
            >
              CG
            </Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight={800} lineHeight={1}>
                CascadeGuard
              </Typography>
              <Typography variant="caption" color="text.secondary">
                AI Operations
              </Typography>
            </Box>
          </Stack>
          <Divider />
        </>
      )}
      <List sx={{ py: 1 }}>
        {navItems.map((item) => (
          <Tooltip
            key={item.id}
            title={!drawerOpen ? item.label : ""}
            placement="right"
          >
            <ListItemButton
              selected={activeTab === item.id}
              onClick={() => onChangeTab(item.id)}
              sx={{ px: 2 }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              {drawerOpen && <ListItemText primary={item.label} />}
            </ListItemButton>
          </Tooltip>
        ))}
      </List>
    </Drawer>
  );
};

export default SideDrawer;
