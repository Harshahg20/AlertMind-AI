import React from "react";
import { Skeleton, Box, Card, CardContent, Grid } from "@mui/material";

const SkeletonLoader = ({
  variant = "card", // card, metric, list, table, chart
  lines = 3,
  height = 200,
  width = "100%",
  showAvatar = false,
  showActions = false,
  gridColumns = 1,
  spacing = 2,
  className = "",
}) => {
  const renderCardSkeleton = () => (
    <Card className={`bg-gray-800 border border-gray-700 ${className}`}>
      <CardContent>
        {showAvatar && (
          <Box display="flex" alignItems="center" mb={2}>
            <Skeleton
              variant="circular"
              width={40}
              height={40}
              sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
            />
            <Box ml={2} flex={1}>
              <Skeleton
                variant="text"
                width="60%"
                height={24}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="40%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
            </Box>
          </Box>
        )}

        <Skeleton
          variant="text"
          width="80%"
          height={28}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
        <Skeleton
          variant="text"
          width="60%"
          height={20}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />

        {Array.from({ length: lines }).map((_, index) => (
          <Skeleton
            key={index}
            variant="text"
            width={index === lines - 1 ? "40%" : "100%"}
            height={16}
            sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
          />
        ))}

        {showActions && (
          <Box display="flex" gap={1} mt={2}>
            <Skeleton
              variant="rectangular"
              width={80}
              height={32}
              sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
            />
            <Skeleton
              variant="rectangular"
              width={80}
              height={32}
              sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );

  const renderMetricSkeleton = () => (
    <Card className={`bg-gray-800 border border-gray-700 ${className}`}>
      <CardContent>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={2}
        >
          <Box flex={1}>
            <Skeleton
              variant="text"
              width="70%"
              height={20}
              sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
            />
            <Skeleton
              variant="text"
              width="50%"
              height={16}
              sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
            />
          </Box>
          <Skeleton
            variant="circular"
            width={48}
            height={48}
            sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
          />
        </Box>
        <Skeleton
          variant="text"
          width="100%"
          height={32}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
        <Skeleton
          variant="text"
          width="60%"
          height={16}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
      </CardContent>
    </Card>
  );

  const renderListSkeleton = () => (
    <Card className={`bg-gray-800 border border-gray-700 ${className}`}>
      <CardContent>
        <Skeleton
          variant="text"
          width="60%"
          height={24}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
        <Box mt={2}>
          {Array.from({ length: lines }).map((_, index) => (
            <Box key={index} display="flex" alignItems="center" mb={1}>
              <Skeleton
                variant="circular"
                width={8}
                height={8}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="80%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)", ml: 1 }}
              />
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );

  const renderTableSkeleton = () => (
    <Card className={`bg-gray-800 border border-gray-700 ${className}`}>
      <CardContent>
        <Skeleton
          variant="text"
          width="40%"
          height={24}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
        <Box mt={2}>
          {Array.from({ length: lines }).map((_, index) => (
            <Box
              key={index}
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              mb={1}
            >
              <Skeleton
                variant="text"
                width="30%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="20%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="25%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );

  const renderChartSkeleton = () => (
    <Card className={`bg-gray-800 border border-gray-700 ${className}`}>
      <CardContent>
        <Skeleton
          variant="text"
          width="50%"
          height={24}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
        <Skeleton
          variant="rectangular"
          width="100%"
          height={height - 100}
          sx={{ bgcolor: "rgba(255,255,255,0.1)", mt: 2 }}
        />
        <Box display="flex" justifyContent="space-between" mt={2}>
          <Skeleton
            variant="text"
            width="20%"
            height={16}
            sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
          />
          <Skeleton
            variant="text"
            width="20%"
            height={16}
            sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
          />
          <Skeleton
            variant="text"
            width="20%"
            height={16}
            sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
          />
        </Box>
      </CardContent>
    </Card>
  );

  const renderGridSkeleton = () => (
    <Box
      display="grid"
      gridTemplateColumns={`repeat(${gridColumns}, 1fr)`}
      gap={spacing}
      className={className}
    >
      {Array.from({ length: gridColumns * 2 }).map((_, index) => (
        <SkeletonLoader
          key={index}
          variant={variant}
          lines={lines}
          height={height}
          showAvatar={showAvatar}
          showActions={showActions}
        />
      ))}
    </Box>
  );

  // Main render logic
  if (gridColumns > 1) {
    return renderGridSkeleton();
  }

  switch (variant) {
    case "metric":
      return renderMetricSkeleton();
    case "list":
      return renderListSkeleton();
    case "table":
      return renderTableSkeleton();
    case "chart":
      return renderChartSkeleton();
    case "card":
    default:
      return renderCardSkeleton();
  }
};

// Predefined skeleton configurations for common use cases
export const AgentControlSkeleton = () => (
  <Box className="space-y-6">
    {/* Agent Management Header */}
    <SkeletonLoader variant="card" lines={4} height={180} showActions={true} />

    {/* Training Status */}
    <SkeletonLoader variant="card" lines={3} height={200} />

    {/* Agent Status Indicators */}
    <SkeletonLoader gridColumns={4} variant="metric" height={120} />

    {/* Agent Metrics */}
    <SkeletonLoader variant="card" lines={6} height={300} />

    {/* Agent Insights */}
    <SkeletonLoader variant="card" lines={8} height={400} />

    {/* Agent Predictions */}
    <SkeletonLoader variant="card" lines={5} height={250} />

    {/* Simulation Controls */}
    <SkeletonLoader gridColumns={4} variant="card" height={150} />
  </Box>
);

export const AlertFeedSkeleton = () => (
  <Box className="space-y-6">
    {/* Header */}
    <SkeletonLoader variant="card" lines={4} height={200} />

    {/* Critical Alerts */}
    <SkeletonLoader variant="list" lines={5} height={300} />

    {/* Filtered Noise */}
    <SkeletonLoader variant="list" lines={3} height={200} />
  </Box>
);

export const CascadeMapSkeleton = () => (
  <Box className="space-y-6">
    {/* Header */}
    <SkeletonLoader variant="card" lines={2} height={120} showActions={true} />

    {/* Enhanced Predictions */}
    <SkeletonLoader variant="card" lines={8} height={500} />
  </Box>
);

export const SystemHealthSkeleton = () => (
  <Box className="space-y-6">
    {/* Header */}
    <SkeletonLoader variant="card" lines={2} height={120} showActions={true} />

    {/* System Overview Grid */}
    <SkeletonLoader gridColumns={4} variant="metric" height={200} />

    {/* Network I/O */}
    <SkeletonLoader variant="card" lines={4} height={200} />

    {/* Service Health */}
    <SkeletonLoader gridColumns={4} variant="card" height={150} />
  </Box>
);

export const DashboardSkeleton = () => (
  <Box className="space-y-6">
    {/* Navigation */}
    <SkeletonLoader variant="card" lines={1} height={60} />

    {/* Key Metrics Row */}
    <SkeletonLoader gridColumns={4} variant="metric" height={150} />

    {/* High-Risk Cascade Alerts */}
    <SkeletonLoader variant="card" lines={6} height={300} />

    {/* Main Dashboard Grid */}
    <SkeletonLoader gridColumns={2} variant="card" height={250} />

    {/* Cross-Client Intelligence */}
    <SkeletonLoader variant="card" lines={4} height={200} />
  </Box>
);

export const AIInsightsSkeleton = () => (
  <Box className="space-y-6">
    {/* Header */}
    <SkeletonLoader variant="card" lines={2} height={120} />

    {/* Tab Navigation */}
    <SkeletonLoader variant="card" lines={1} height={60} />

    {/* Overview Grid */}
    <SkeletonLoader gridColumns={3} variant="card" height={200} />

    {/* Live Prediction */}
    <SkeletonLoader variant="card" lines={8} height={400} />
  </Box>
);

export const ClientCascadeSkeleton = () => (
  <Box className="space-y-6">
    {/* Header */}
    <SkeletonLoader variant="card" lines={2} height={120} showActions={true} />

    {/* Client Selector and View Toggle */}
    <SkeletonLoader variant="card" lines={1} height={80} />

    {/* Client Risk Overview Grid */}
    <SkeletonLoader gridColumns={3} variant="card" height={300} />
  </Box>
);

export const AppLoadingSkeleton = () => (
  <Box className="min-h-screen bg-gray-900 flex items-center justify-center">
    <Box className="text-center space-y-6">
      <Card className="bg-gray-800 border border-gray-700">
        <CardContent>
          <Skeleton
            variant="text"
            width="80%"
            height={28}
            sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
          />
          <Skeleton
            variant="text"
            width="60%"
            height={20}
            sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
          />
          <Skeleton
            variant="text"
            width="100%"
            height={16}
            sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
          />
        </CardContent>
      </Card>
      <Skeleton
        variant="text"
        width="60%"
        height={24}
        sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
      />
    </Box>
  </Box>
);

export const EnhancedPatchSkeleton = () => (
  <Box className="space-y-6">
    {/* Header */}
    <Box className="flex items-center justify-between">
      <Box>
        <Skeleton
          variant="text"
          width={300}
          height={32}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
        <Skeleton
          variant="text"
          width={400}
          height={20}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
      </Box>
      <Skeleton
        variant="rectangular"
        width={120}
        height={40}
        sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
      />
    </Box>

    {/* Tabs */}
    <Box className="flex space-x-4">
      {[1, 2, 3, 4].map((i) => (
        <Skeleton
          key={i}
          variant="rectangular"
          width={120}
          height={40}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
      ))}
    </Box>

    {/* Content Grid */}
    <Grid container spacing={3}>
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Grid item xs={12} md={6} lg={4} key={i}>
          <Card className="bg-gray-800 border border-gray-700">
            <CardContent>
              <Skeleton
                variant="text"
                width="80%"
                height={24}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="60%"
                height={20}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="100%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="90%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  </Box>
);

export const ITAdminSkeleton = () => (
  <Box className="space-y-6">
    {/* Header */}
    <Box className="flex items-center justify-between">
      <Box>
        <Skeleton
          variant="text"
          width={350}
          height={32}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
        <Skeleton
          variant="text"
          width={500}
          height={20}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
      </Box>
      <Skeleton
        variant="rectangular"
        width={120}
        height={40}
        sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
      />
    </Box>

    {/* Tabs */}
    <Box className="flex space-x-4">
      {[1, 2, 3, 4, 5].map((i) => (
        <Skeleton
          key={i}
          variant="rectangular"
          width={140}
          height={40}
          sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
        />
      ))}
    </Box>

    {/* Content Grid */}
    <Grid container spacing={3}>
      {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
        <Grid item xs={12} md={6} lg={4} key={i}>
          <Card className="bg-gray-800 border border-gray-700">
            <CardContent>
              <Box className="flex items-center justify-between mb-3">
                <Skeleton
                  variant="text"
                  width="60%"
                  height={20}
                  sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
                />
                <Skeleton
                  variant="rectangular"
                  width={60}
                  height={24}
                  sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
                />
              </Box>
              <Skeleton
                variant="text"
                width="100%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="90%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Skeleton
                variant="text"
                width="80%"
                height={16}
                sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
              />
              <Box className="mt-3">
                <Skeleton
                  variant="rectangular"
                  width="100%"
                  height={32}
                  sx={{ bgcolor: "rgba(255,255,255,0.1)" }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  </Box>
);

// Export SkeletonLoader as a named export
export { SkeletonLoader };

export default SkeletonLoader;
