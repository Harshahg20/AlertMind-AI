import React from "react";
import {
  Box,
  Container,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Typography,
  Stack,
  Chip,
  LinearProgress,
  Avatar,
  Divider,
  Tooltip,
  Skeleton,
  useTheme,
} from "@mui/material";
import InsightsIcon from "@mui/icons-material/Insights";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import BoltIcon from "@mui/icons-material/Bolt";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import LanIcon from "@mui/icons-material/Lan";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";
import CategoryIcon from "@mui/icons-material/Category";
import LinkIcon from "@mui/icons-material/Link";
import ScheduleIcon from "@mui/icons-material/Schedule";
import { DataGrid } from "@mui/x-data-grid";

const Dashboard = ({ stats, alerts, predictions, filteredData, loading }) => {
  const theme = useTheme();
  const isLoading = !!loading;

  const highRiskPredictions = (predictions || []).filter(
    (p) => p.prediction_confidence > 0.7 && p.time_to_cascade_minutes < 20
  );

  const criticalAlerts = (alerts || []).filter(
    (a) => a.severity === "critical"
  );

  const formatTime = (value) => {
    try {
      return new Date(value).toLocaleTimeString();
    } catch (e) {
      return "-";
    }
  };

  const metricCard = (icon, label, value, chip, gradient) => (
    <Card
      elevation={0}
      sx={{
        bgcolor: "transparent",
        borderRadius: 3,
        overflow: "hidden",
        border: `1px solid ${theme.palette.primary.main}20`,
        backdropFilter: "blur(8px)",
        background:
          gradient ||
          `linear-gradient(180deg, ${theme.palette.background.paper}80 0%, ${theme.palette.background.paper} 60%)`,
      }}
    >
      <CardContent>
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
        >
          <Stack spacing={0.5}>
            <Typography
              variant="body2"
              sx={{
                color: "text.secondary",
                textTransform: "uppercase",
                letterSpacing: 0.5,
              }}
            >
              {label}
            </Typography>
            <Typography variant="h4" fontWeight={800}>
              {isLoading ? <Skeleton width={80} /> : value}
            </Typography>
          </Stack>
          <Avatar
            sx={{
              bgcolor: `${theme.palette.primary.main}33`,
              color: "primary.main",
              boxShadow: 0,
            }}
          >
            {icon}
          </Avatar>
        </Stack>
        {isLoading ? (
          <Skeleton variant="text" width={140} sx={{ mt: 2 }} />
        ) : (
          chip
        )}
      </CardContent>
    </Card>
  );

  const recentAlertsColumns = [
    { field: "client_name", headerName: "Client", flex: 1, minWidth: 140 },
    { field: "system", headerName: "System", flex: 1, minWidth: 120 },
    {
      field: "message",
      headerName: "Message",
      flex: 2,
      minWidth: 240,
      renderCell: (params) => (
        <Tooltip title={params.value} placement="top-start">
          <Typography variant="body2" noWrap>
            {params.value}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: "cascade_risk",
      headerName: "Cascade Risk",
      width: 150,
      renderCell: (params) => (
        <Stack
          direction="row"
          spacing={1}
          alignItems="center"
          sx={{ width: "100%" }}
        >
          <Box sx={{ flex: 1 }}>
            <LinearProgress
              variant="determinate"
              value={Math.round((params.value || 0) * 100)}
              color={
                params.value > 0.7
                  ? "error"
                  : params.value > 0.5
                  ? "warning"
                  : "info"
              }
              sx={{ height: 8, borderRadius: 5 }}
            />
          </Box>
          <Typography variant="caption" sx={{ width: 36, textAlign: "right" }}>
            {Math.round((params.value || 0) * 100)}%
          </Typography>
        </Stack>
      ),
    },
    {
      field: "timestamp",
      headerName: "Time",
      width: 120,
      valueGetter: (p) => formatTime(p.value),
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3, px: { xs: 2, sm: 3, md: 4 } }}>
      <Grid container spacing={2} alignItems="stretch">
        <Grid item xs={12} sm={6} md={4} lg={3} xl={3}>
          {metricCard(
            <InsightsIcon />,
            "Total Alerts",
            stats?.total_alerts ?? 0,
            filteredData ? (
              <Chip
                size="small"
                sx={{ mt: 2 }}
                color="success"
                label={`↓ ${filteredData.summary.noise_reduction_percent}% noise filtered`}
              />
            ) : null,
            `linear-gradient(180deg, ${theme.palette.primary.main}22 0%, ${theme.palette.background.paper} 60%)`
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={3} xl={3}>
          {metricCard(
            <WarningAmberIcon />,
            "Critical Alerts",
            stats?.critical_alerts ?? 0,
            <Chip
              size="small"
              sx={{ mt: 2 }}
              color="error"
              label={`${stats?.critical_percentage ?? 0}% of total`}
            />,
            `linear-gradient(180deg, ${theme.palette.error.main}22 0%, ${theme.palette.background.paper} 60%)`
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={3} xl={3}>
          {metricCard(
            <BoltIcon />,
            "Active Predictions",
            (predictions || []).length,
            <Chip
              size="small"
              sx={{ mt: 2 }}
              color="warning"
              label={`${highRiskPredictions.length} high-risk`}
            />,
            `linear-gradient(180deg, ${theme.palette.warning.main}22 0%, ${theme.palette.background.paper} 60%)`
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={3} xl={3}>
          {metricCard(
            <TrendingUpIcon />,
            "Efficiency Gain",
            `${
              filteredData ? filteredData.summary.noise_reduction_percent : 0
            }%`,
            <Chip
              size="small"
              sx={{ mt: 2 }}
              color="info"
              label="Alert noise reduction"
            />,
            `linear-gradient(180deg, ${theme.palette.info.main}22 0%, ${theme.palette.background.paper} 60%)`
          )}
        </Grid>
      </Grid>

      <Box sx={{ height: 16 }} />

      {!isLoading && highRiskPredictions.length > 0 && (
        <Card
          elevation={0}
          sx={{
            mb: 3,
            borderRadius: 3,
            border: `1px solid ${theme.palette.error.main}22`,
            background: `linear-gradient(180deg, ${theme.palette.error.main}11 0%, ${theme.palette.background.paper} 60%)`,
            backdropFilter: "blur(8px)",
          }}
        >
          <CardHeader
            avatar={<LanIcon color="error" />}
            title={
              <Typography variant="h6" fontWeight={800}>
                URGENT: High-Risk Cascade Predictions
              </Typography>
            }
            subheader={
              <Typography variant="body2" color="text.secondary">
                Immediate attention recommended
              </Typography>
            }
          />
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} mb={2}>
              <Chip
                size="small"
                color="error"
                label={`${highRiskPredictions.length} items`}
              />
            </Stack>
            <Grid container spacing={2}>
              {highRiskPredictions.slice(0, 3).map((prediction) => {
                const relatedAlert = (alerts || []).find(
                  (a) => a.id === prediction.alert_id
                );
                return (
                  <Grid item xs={12} md={4} key={prediction.alert_id}>
                    <Card
                      variant="outlined"
                      sx={{ borderColor: `${theme.palette.error.main}33` }}
                    >
                      <CardContent>
                        <Stack
                          direction="row"
                          alignItems="center"
                          justifyContent="space-between"
                          mb={1.5}
                        >
                          <Stack
                            direction="row"
                            spacing={1}
                            alignItems="center"
                          >
                            <Box
                              sx={{
                                width: 8,
                                height: 8,
                                bgcolor: "error.main",
                                borderRadius: 10,
                              }}
                            />
                            <Typography
                              variant="subtitle2"
                              fontWeight={600}
                              noWrap
                            >
                              {relatedAlert
                                ? `${relatedAlert.client_name} — ${relatedAlert.system}`
                                : "Unknown Alert"}
                            </Typography>
                          </Stack>
                          <Chip
                            size="small"
                            color="warning"
                            icon={<ScheduleIcon fontSize="small" />}
                            label={`${prediction.time_to_cascade_minutes} min`}
                          />
                        </Stack>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          gutterBottom
                          noWrap
                        >
                          {relatedAlert?.message ?? "Alert details unavailable"}
                        </Typography>
                        <Stack
                          direction="row"
                          alignItems="center"
                          justifyContent="space-between"
                        >
                          <Typography variant="caption" color="text.secondary">
                            Will affect:{" "}
                            {prediction.predicted_cascade_systems.join(", ")}
                          </Typography>
                          <Chip
                            size="small"
                            color="error"
                            label={`${Math.round(
                              prediction.prediction_confidence * 100
                            )}%`}
                          />
                        </Stack>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </CardContent>
        </Card>
      )}

      <Grid container spacing={2} alignItems="stretch">
        <Grid item xs={12} md={6} sx={{ display: "flex" }}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 3,
              border: `1px solid ${theme.palette.primary.main}22`,
              backdropFilter: "blur(8px)",
              display: "flex",
              flexDirection: "column",
              flex: 1,
              minHeight: { xs: 360, md: 420 },
            }}
          >
            <CardHeader
              avatar={<InsightsIcon color="primary" />}
              title={
                <Typography variant="h6" fontWeight={800}>
                  Alert Intelligence Summary
                </Typography>
              }
              subheader={
                <Typography variant="body2" color="text.secondary">
                  Automated insights from AI filtering & correlation
                </Typography>
              }
            />
            <CardContent>
              {filteredData ? (
                <Stack spacing={1.5}>
                  <Stack
                    direction="row"
                    alignItems="center"
                    justifyContent="space-between"
                  >
                    <Typography color="text.secondary">
                      Original Alerts
                    </Typography>
                    <Typography fontWeight={600}>
                      {filteredData.summary.total_alerts}
                    </Typography>
                  </Stack>
                  <Stack
                    direction="row"
                    alignItems="center"
                    justifyContent="space-between"
                  >
                    <Typography color="text.secondary">
                      After AI Filtering
                    </Typography>
                    <Typography color="success.main" fontWeight={600}>
                      {filteredData.summary.critical_alerts}
                    </Typography>
                  </Stack>
                  <Stack
                    direction="row"
                    alignItems="center"
                    justifyContent="space-between"
                  >
                    <Typography color="text.secondary">
                      Correlated Groups
                    </Typography>
                    <Typography color="info.main" fontWeight={600}>
                      {filteredData.summary.correlated_groups}
                    </Typography>
                  </Stack>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    Processing Impact
                  </Typography>
                  <Typography variant="body2" color="success.light">
                    {filteredData.summary.efficiency_improvement}
                  </Typography>
                  <Typography variant="caption" color="text.disabled">
                    Processing time: {filteredData.total_processing_time_ms}ms
                  </Typography>
                </Stack>
              ) : (
                <Stack spacing={1.5}>
                  <Skeleton variant="rounded" height={36} />
                  <Skeleton variant="rounded" height={36} />
                  <Skeleton variant="rounded" height={36} />
                  <Skeleton variant="text" width={160} />
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} sx={{ display: "flex" }}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 3,
              border: `1px solid ${theme.palette.error.main}22`,
              backdropFilter: "blur(8px)",
              display: "flex",
              flexDirection: "column",
              flex: 1,
              minHeight: { xs: 360, md: 420 },
            }}
          >
            <CardHeader
              avatar={<WarningAmberIcon color="error" />}
              title={
                <Typography variant="h6" fontWeight={800}>
                  Recent Critical Alerts
                </Typography>
              }
              subheader={
                <Typography variant="body2" color="text.secondary">
                  Latest incidents requiring attention
                </Typography>
              }
            />
            <CardContent>
              {isLoading ? (
                <Stack spacing={1}>
                  <Skeleton variant="rounded" height={48} />
                  <Skeleton variant="rounded" height={48} />
                  <Skeleton variant="rounded" height={48} />
                  <Skeleton variant="rounded" height={48} />
                </Stack>
              ) : (
                <Box sx={{ height: { xs: 360, md: 420, xl: 520 } }}>
                  <DataGrid
                    autoHeight={false}
                    disableRowSelectionOnClick
                    rows={criticalAlerts.slice(0, 50)}
                    getRowId={(r) => r.id}
                    columns={recentAlertsColumns}
                    pageSizeOptions={[5, 10, 25]}
                    initialState={{
                      pagination: { paginationModel: { pageSize: 10 } },
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} sx={{ display: "flex" }}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 3,
              border: `1px solid ${theme.palette.secondary.main}22`,
              backdropFilter: "blur(8px)",
              display: "flex",
              flexDirection: "column",
              flex: 1,
              minHeight: { xs: 360, md: 420 },
            }}
          >
            <CardHeader
              avatar={<PeopleAltIcon color="secondary" />}
              title={
                <Typography variant="h6" fontWeight={800}>
                  Client Alert Distribution
                </Typography>
              }
              subheader={
                <Typography variant="body2" color="text.secondary">
                  Breakdown of alert load by client
                </Typography>
              }
            />
            <CardContent>
              {isLoading ? (
                <Stack spacing={1.5}>
                  <Skeleton variant="rounded" height={36} />
                  <Skeleton variant="rounded" height={36} />
                  <Skeleton variant="rounded" height={36} />
                </Stack>
              ) : (
                <Stack spacing={2}>
                  {stats?.client_breakdown &&
                    Object.entries(stats.client_breakdown).map(([name, s]) => (
                      <Box key={name}>
                        <Stack
                          direction="row"
                          justifyContent="space-between"
                          mb={0.5}
                        >
                          <Typography variant="body2" fontWeight={600}>
                            {name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {s.total_alerts} alerts
                          </Typography>
                        </Stack>
                        <LinearProgress
                          variant="determinate"
                          value={Math.round(
                            ((s.critical_alerts || 0) / (s.total_alerts || 1)) *
                              100
                          )}
                          color="error"
                          sx={{ height: 8, borderRadius: 6 }}
                        />
                        <Stack direction="row" spacing={2} mt={0.5}>
                          <Chip
                            size="small"
                            color="error"
                            label={`${s.critical_alerts} critical`}
                          />
                          <Chip
                            size="small"
                            color="warning"
                            label={`${s.high_cascade_risk} high-risk`}
                          />
                        </Stack>
                      </Box>
                    ))}
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} sx={{ display: "flex" }}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 3,
              border: `1px solid ${theme.palette.info.main}22`,
              backdropFilter: "blur(8px)",
              display: "flex",
              flexDirection: "column",
              flex: 1,
              minHeight: { xs: 360, md: 420 },
            }}
          >
            <CardHeader
              avatar={<CategoryIcon color="info" />}
              title={
                <Typography variant="h6" fontWeight={800}>
                  Alert Categories
                </Typography>
              }
              subheader={
                <Typography variant="body2" color="text.secondary">
                  Top categories by volume
                </Typography>
              }
            />
            <CardContent>
              {isLoading ? (
                <Stack spacing={1.25}>
                  <Skeleton variant="rounded" height={28} />
                  <Skeleton variant="rounded" height={28} />
                  <Skeleton variant="rounded" height={28} />
                  <Skeleton variant="rounded" height={28} />
                </Stack>
              ) : (
                <Stack spacing={1.25}>
                  {stats?.category_breakdown &&
                    Object.entries(stats.category_breakdown)
                      .sort(([, a], [, b]) => b - a)
                      .slice(0, 6)
                      .map(([category, count]) => (
                        <Stack
                          key={category}
                          direction="row"
                          alignItems="center"
                          justifyContent="space-between"
                        >
                          <Stack
                            direction="row"
                            spacing={1}
                            alignItems="center"
                          >
                            <Box
                              sx={{
                                width: 10,
                                height: 10,
                                borderRadius: 10,
                                bgcolor:
                                  category === "performance"
                                    ? "warning.main"
                                    : category === "security"
                                    ? "error.main"
                                    : category === "network"
                                    ? "info.main"
                                    : category === "storage"
                                    ? "success.main"
                                    : category === "system"
                                    ? "secondary.main"
                                    : "text.disabled",
                              }}
                            />
                            <Typography
                              className="capitalize"
                              color="text.secondary"
                            >
                              {category}
                            </Typography>
                          </Stack>
                          <Typography fontWeight={600}>{count}</Typography>
                        </Stack>
                      ))}
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ height: 16 }} />

      <Card
        elevation={0}
        sx={{
          borderRadius: 3,
          border: `1px solid ${theme.palette.primary.main}22`,
          backdropFilter: "blur(8px)",
        }}
      >
        <CardHeader
          avatar={<LinkIcon color="primary" />}
          title={
            <Typography variant="h6" fontWeight={800}>
              Cross-Client Intelligence Active
            </Typography>
          }
          subheader={
            <Typography variant="body2" color="text.secondary">
              Learning patterns from all clients
            </Typography>
          }
        />
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="overline" color="text.secondary">
                    Avg Confidence
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    {Math.round(
                      ((predictions || []).reduce(
                        (acc, p) => acc + p.prediction_confidence,
                        0
                      ) /
                        ((predictions || []).length || 1)) *
                        100
                    ) || 0}
                    %
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="overline" color="text.secondary">
                    Urgent (&lt;15min)
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    {
                      (predictions || []).filter(
                        (p) => p.time_to_cascade_minutes < 15
                      ).length
                    }
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="overline" color="text.secondary">
                    Systems at Risk
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    {(predictions || []).reduce(
                      (acc, p) => acc + p.predicted_cascade_systems.length,
                      0
                    )}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
};

export default Dashboard;
