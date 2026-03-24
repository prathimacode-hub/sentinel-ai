import React, { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

function Analytics({ events }) {
  // -----------------------------
  // COMPUTE ANALYTICS DATA
  // -----------------------------
  const analyticsData = useMemo(() => {
    const total = events.length;

    const high = events.filter((e) => e.level === "HIGH").length;
    const medium = events.filter((e) => e.level === "MEDIUM").length;
    const low = events.filter((e) => e.level === "LOW").length;

    const riskScore = (high * 2 + medium) / (total || 1);

    const studentMap = {};
    events.forEach((e) => {
      const id = e.student_id || "Unknown";
      studentMap[id] = (studentMap[id] || 0) + 1;
    });

    const studentData = Object.keys(studentMap).map((id) => ({
      student: `Student ${id}`,
      alerts: studentMap[id],
    }));

    return {
      total,
      high,
      medium,
      low,
      riskScore,
      chartData: [
        { name: "High", value: high },
        { name: "Medium", value: medium },
        { name: "Low", value: low },
      ],
      studentData,
    };
  }, [events]);

  const COLORS = ["#ef4444", "#f59e0b", "#22c55e"];

  // -----------------------------
  // RISK STATUS
  // -----------------------------
  const getRiskMessage = () => {
    if (analyticsData.riskScore > 1.2)
      return "⚠ High cheating risk detected";
    if (analyticsData.riskScore > 0.6)
      return "⚠ Moderate suspicious activity";
    return "✅ System stable";
  };

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="analytics">
      <h2>📊 SentinelAI Analytics Dashboard</h2>

      {/* -----------------------------
          SUMMARY CARDS
      ----------------------------- */}
      <div className="grid">
        <div className="tile">
          <h3>Total Events</h3>
          <p>{analyticsData.total}</p>
        </div>

        <div className="tile high">
          <h3>High Alerts</h3>
          <p>{analyticsData.high}</p>
        </div>

        <div className="tile medium">
          <h3>Medium Alerts</h3>
          <p>{analyticsData.medium}</p>
        </div>

        <div className="tile safe">
          <h3>Low Alerts</h3>
          <p>{analyticsData.low}</p>
        </div>
      </div>

      {/* -----------------------------
          RISK SCORE
      ----------------------------- */}
      <div className="tile" style={{ marginTop: "20px", transition: "all 0.5s ease" }}>
        <h3>Overall Risk Score</h3>
        <p style={{ fontSize: "20px", fontWeight: "bold" }}>
          {analyticsData.riskScore.toFixed(2)}
        </p>
        <p>{getRiskMessage()}</p>
      </div>

      {/* -----------------------------
          BAR CHART: Risk Level Distribution
      ----------------------------- */}
      <div className="tile" style={{ marginTop: "20px" }}>
        <h3>Risk Level Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={analyticsData.chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar
              dataKey="value"
              isAnimationActive={true}
              animationDuration={800}
            >
              {analyticsData.chartData.map((entry, index) => (
                <Cell key={index} fill={COLORS[index]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* -----------------------------
          PIE CHART: Risk Distribution
      ----------------------------- */}
      <div className="tile" style={{ marginTop: "20px" }}>
        <h3>Risk Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={analyticsData.chartData}
              dataKey="value"
              outerRadius={100}
              label={({ name, percent }) =>
                `${name}: ${(percent * 100).toFixed(0)}%`
              }
              isAnimationActive={true}
            >
              {analyticsData.chartData.map((_, index) => (
                <Cell key={index} fill={COLORS[index]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* -----------------------------
          STUDENT ALERT TREND
      ----------------------------- */}
      <div className="tile" style={{ marginTop: "20px" }}>
        <h3>Student Alert Trend</h3>
        {analyticsData.studentData.length === 0 ? (
          <p>No student activity yet</p>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analyticsData.studentData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="student" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="alerts"
                fill="#22c55e"
                isAnimationActive={true}
                animationDuration={800}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

export default Analytics;