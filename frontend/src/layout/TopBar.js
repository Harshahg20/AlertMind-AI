import React from "react";
import {
  AppBar,
  Toolbar,
  Stack,
  IconButton,
  Avatar,
  Typography,
  Chip,
  useTheme,
} from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import InsightsIcon from "@mui/icons-material/Insights";
import BoltIcon from "@mui/icons-material/Bolt";
import MenuIcon from "@mui/icons-material/Menu";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import { drawerWidthExpanded, drawerWidthCollapsed } from "./constants";

const TopBar = ({ drawerOpen, onToggleDrawer, stats, predictions }) => {
  const theme = useTheme();
  return (
    <AppBar
      position="fixed"
      color="transparent"
      elevation={0}
      sx={{
        backdropFilter: "blur(10px)",
        background:
          "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%)",
        borderBottom: `1px solid ${theme.palette.primary.main}22`,
        width: {
          xs: "100%",
          lg: `calc(100% - ${
            drawerOpen ? drawerWidthExpanded : drawerWidthCollapsed
          }px)`,
        },
        ml: {
          lg: `${drawerOpen ? drawerWidthExpanded : drawerWidthCollapsed}px`,
        },
      }}
    >
      <Toolbar
        sx={{
          display: "flex",
          justifyContent: "space-between",
          gap: 2,
          minHeight: 40,
          py: 0.5,
        }}
      >
        <Stack direction="row" spacing={2} alignItems="center">
          <IconButton color="inherit" onClick={onToggleDrawer}>
            {drawerOpen ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
          {!drawerOpen && (
            <Stack direction="row" spacing={1.5} alignItems="center">
              <Avatar
                sx={{
                  bgcolor: "primary.dark",
                  backgroundImage: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                  width: 24,
                  height: 24,
                  fontWeight: 800,
                  fontSize: 12,
                }}
              >
                CG
              </Avatar>
              <Typography variant="caption" fontWeight={800}>
                CascadeGuard
              </Typography>
            </Stack>
          )}
        </Stack>

        <Stack direction="row" spacing={2} alignItems="center">
          {stats?.total_alerts > 0 && (
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                size="small"
                color="error"
                icon={<WarningAmberIcon fontSize="small" />}
                label={`${stats.critical_alerts} Critical`}
              />
              <Chip
                size="small"
                color="warning"
                icon={<InsightsIcon fontSize="small" />}
                label={`${stats.warning_alerts} Warning`}
              />
              <Chip
                size="small"
                color="info"
                icon={<BoltIcon fontSize="small" />}
                label={`${predictions?.length || 0} Predictions`}
              />
            </Stack>
          )}
          <Chip size="small" color="success" label="Live" />
        </Stack>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
