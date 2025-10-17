import React from "react";
import EnhancedCascadeMap from "../components/EnhancedCascadeMap";

const CascadeMap = ({ predictions, clients, loading }) => {
  return (
    <EnhancedCascadeMap
      predictions={predictions}
      clients={clients}
      loading={loading}
    />
  );
};

export default CascadeMap;
