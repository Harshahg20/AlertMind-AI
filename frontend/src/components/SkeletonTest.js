import React from "react";
import {
  SkeletonLoader,
  AgentControlSkeleton,
  AlertFeedSkeleton,
  CascadeMapSkeleton,
  SystemHealthSkeleton,
  DashboardSkeleton,
  AIInsightsSkeleton,
} from "./SkeletonLoader";

const SkeletonTest = () => {
  return (
    <div className="p-6 space-y-8 bg-gray-900 min-h-screen">
      <h1 className="text-2xl font-bold text-white mb-6">
        Skeleton Loader Test
      </h1>

      {/* Basic Skeleton Variants */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Basic Variants</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <SkeletonLoader variant="card" lines={3} height={200} />
          <SkeletonLoader variant="metric" height={150} />
          <SkeletonLoader variant="list" lines={4} height={180} />
        </div>
      </div>

      {/* Grid Layouts */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Grid Layouts</h2>
        <SkeletonLoader gridColumns={4} variant="metric" height={120} />
      </div>

      {/* Module-Specific Skeletons */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-white">
          Module-Specific Skeletons
        </h2>

        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-300">Agent Control</h3>
          <AgentControlSkeleton />
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-300">Alert Feed</h3>
          <AlertFeedSkeleton />
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-300">Cascade Map</h3>
          <CascadeMapSkeleton />
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-300">System Health</h3>
          <SystemHealthSkeleton />
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-300">Dashboard</h3>
          <DashboardSkeleton />
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-300">AI Insights</h3>
          <AIInsightsSkeleton />
        </div>
      </div>
    </div>
  );
};

export default SkeletonTest;
