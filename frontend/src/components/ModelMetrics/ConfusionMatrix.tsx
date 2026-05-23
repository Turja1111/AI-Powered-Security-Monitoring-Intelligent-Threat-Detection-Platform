import React from "react";

export const ConfusionMatrix: React.FC = () => {
  const classes = ["BENIGN", "DDoS", "PortScan", "BruteForce", "WebAttack"];
  
  // Matrix coordinates represent [actual][predicted] percentages/counts
  const matrixData = [
    [0.992, 0.003, 0.002, 0.001, 0.002], // BENIGN
    [0.004, 0.988, 0.005, 0.001, 0.002], // DDoS
    [0.003, 0.002, 0.994, 0.001, 0.000], // PortScan
    [0.008, 0.002, 0.002, 0.985, 0.003], // BruteForce
    [0.015, 0.005, 0.000, 0.010, 0.970]  // WebAttack
  ];

  const getCellBg = (val: number) => {
    if (val > 0.90) return "bg-blue-600/90 text-white";
    if (val > 0.50) return "bg-blue-500/60 text-white";
    if (val > 0.10) return "bg-blue-500/30 text-blue-200";
    if (val > 0.01) return "bg-[#1e2d4a]/40 text-[#64748b]";
    return "bg-[#0a0e1a]/60 text-[#64748b]/40";
  };

  return (
    <div className="glass-card p-6 h-[400px] flex flex-col justify-between">
      <div>
        <h3 className="text-md font-bold text-white font-mono uppercase tracking-wider">Confusion Matrix</h3>
        <p className="text-xs text-[#64748b]">Multi-class classification error distributions</p>
      </div>

      <div className="flex-1 mt-6 flex flex-col justify-center">
        <div className="max-w-[460px] mx-auto w-full font-mono text-[10px]">
          {/* Header Row */}
          <div className="grid grid-cols-[80px_repeat(5,1fr)] gap-1.5 mb-1.5 text-center text-[#64748b] font-semibold">
            <div className="text-left">Actual \ Pred</div>
            {classes.map(c => (
              <div key={c} className="truncate" title={c}>{c}</div>
            ))}
          </div>

          {/* Matrix Rows */}
          <div className="space-y-1.5">
            {classes.map((actualClass, actIdx) => (
              <div key={actualClass} className="grid grid-cols-[80px_repeat(5,1fr)] gap-1.5 items-center">
                {/* Y-axis actual label */}
                <div className="text-[#94a3b8] font-semibold text-left truncate" title={actualClass}>
                  {actualClass}
                </div>
                
                {/* Predicted cells */}
                {matrixData[actIdx].map((val, predIdx) => (
                  <div
                    key={`${actIdx}-${predIdx}`}
                    className={`h-12 flex items-center justify-center rounded border border-[#1e2d4a]/25 text-xs font-bold transition-all hover:scale-[1.05] relative group cursor-pointer ${getCellBg(val)}`}
                  >
                    <span>{(val * 100).toFixed(1)}%</span>
                    
                    {/* Tooltip */}
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-[#0a0e1a] text-white border border-[#1e2d4a] py-1.5 px-2.5 rounded text-[10px] opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-xl whitespace-nowrap">
                      Actual: {actualClass} | Predicted: {classes[predIdx]} ({(val * 100).toFixed(2)}%)
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
