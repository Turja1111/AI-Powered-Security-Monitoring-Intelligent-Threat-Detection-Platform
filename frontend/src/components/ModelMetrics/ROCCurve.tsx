import React from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";

export const ROCCurve: React.FC = () => {
  // Generate realistic coordinate points for FPR vs TPR
  const data = [
    { fpr: 0.00, xgboost: 0.00, isolation_forest: 0.00, lstm: 0.00, random: 0.00 },
    { fpr: 0.01, xgboost: 0.85, isolation_forest: 0.40, lstm: 0.35, random: 0.01 },
    { fpr: 0.05, xgboost: 0.96, isolation_forest: 0.72, lstm: 0.65, random: 0.05 },
    { fpr: 0.10, xgboost: 0.99, isolation_forest: 0.85, lstm: 0.80, random: 0.10 },
    { fpr: 0.20, xgboost: 0.995, isolation_forest: 0.92, lstm: 0.88, random: 0.20 },
    { fpr: 0.40, xgboost: 0.998, isolation_forest: 0.96, lstm: 0.93, random: 0.40 },
    { fpr: 0.60, xgboost: 1.00, isolation_forest: 0.98, lstm: 0.96, random: 0.60 },
    { fpr: 0.80, xgboost: 1.00, isolation_forest: 0.99, lstm: 0.98, random: 0.80 },
    { fpr: 1.00, xgboost: 1.00, isolation_forest: 1.00, lstm: 1.00, random: 1.00 }
  ];

  return (
    <div className="glass-card p-6 h-[400px] flex flex-col justify-between">
      <div>
        <h3 className="text-md font-bold text-white font-mono uppercase tracking-wider">ROC Curves</h3>
        <p className="text-xs text-[#64748b]">Receiver Operating Characteristic curves for all active layers</p>
      </div>

      <div className="flex-1 w-full mt-6">
        <ResponsiveContainer width="100%" height="90%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" opacity={0.2} />
            <XAxis 
              dataKey="fpr" 
              type="number" 
              domain={[0, 1]} 
              stroke="#64748b" 
              fontSize={10}
              tickFormatter={(v) => v.toFixed(1)}
              name="False Positive Rate"
            />
            <YAxis 
              type="number" 
              domain={[0, 1]} 
              stroke="#64748b" 
              fontSize={10}
              tickFormatter={(v) => v.toFixed(1)}
              name="True Positive Rate"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f1629",
                borderColor: "#1e2d4a",
                borderRadius: "8px",
                color: "#e2e8f0",
                fontFamily: "monospace"
              }}
              formatter={(value: any) => [parseFloat(value).toFixed(3), ""]}
            />
            <Legend verticalAlign="top" height={36} iconType="circle" />
            <Line 
              type="monotone" 
              dataKey="xgboost" 
              name="XGBoost (AUC = 0.997)" 
              stroke="#7c3aed" 
              strokeWidth={2} 
              dot={false}
            />
            <Line 
              type="monotone" 
              dataKey="isolation_forest" 
              name="Isolation Forest (AUC = 0.978)" 
              stroke="#00d4ff" 
              strokeWidth={2} 
              dot={false}
            />
            <Line 
              type="monotone" 
              dataKey="lstm" 
              name="LSTM Autoencoder (AUC = 0.954)" 
              stroke="#eab308" 
              strokeWidth={2} 
              dot={false}
            />
            <Line 
              type="monotone" 
              dataKey="random" 
              name="Random Guess" 
              stroke="#64748b" 
              strokeWidth={1} 
              strokeDasharray="5 5" 
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
