import React from "react";
import { MLModel } from "../../types";
import { Brain, Calendar, Database, Play } from "lucide-react";

interface ModelCardProps {
  model: MLModel;
  onRetrain?: (name: string) => void;
}

export const ModelCard: React.FC<ModelCardProps> = ({ model, onRetrain }) => {
  const getMetricPercentage = (val: number) => {
    return `${(val * 100).toFixed(1)}%`;
  };

  return (
    <div className={`glass-card p-6 border transition-all duration-300 relative ${
      model.is_active 
        ? "border-[#00d4ff]/40 shadow-[0_0_20px_rgba(0,212,255,0.08)] bg-gradient-to-br from-[#0f1629] to-[#162035]/60" 
        : "border-[#1e2d4a]/40"
    }`}>
      {/* Active Indicator */}
      <div className="absolute top-6 right-6 flex items-center gap-2">
        <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border uppercase ${
          model.is_active 
            ? "text-[#10b981] bg-[#10b981]/10 border-[#10b981]/30" 
            : "text-[#64748b] bg-slate-900/40 border-slate-500/20"
        }`}>
          {model.is_active ? "Active serving" : "Inactive"}
        </span>
      </div>

      {/* Title block */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-[#0a0e1a] rounded-xl border border-[#1e2d4a]/50 text-[#00d4ff]">
          <Brain className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-md font-bold text-white uppercase font-mono tracking-wider">{model.model_name.replace("_", " ")}</h3>
          <span className="text-xs text-[#64748b]">v{model.version} — {model.algorithm}</span>
        </div>
      </div>

      {/* Metrics breakdown */}
      <div className="grid grid-cols-2 gap-4 font-mono text-xs mb-6">
        {/* F1 Score */}
        <div className="bg-[#0a0e1a]/55 p-3 rounded-lg border border-[#1e2d4a]/30">
          <span className="text-[#64748b] text-[10px] block uppercase tracking-wider">F1-Score</span>
          <span className="text-lg font-bold text-white">{model.f1_score.toFixed(3)}</span>
          <div className="w-full bg-[#162035] h-1 rounded-full mt-2 overflow-hidden">
            <div className="bg-[#00d4ff] h-full" style={{ width: getMetricPercentage(model.f1_score) }} />
          </div>
        </div>

        {/* Precision */}
        <div className="bg-[#0a0e1a]/55 p-3 rounded-lg border border-[#1e2d4a]/30">
          <span className="text-[#64748b] text-[10px] block uppercase tracking-wider">Precision</span>
          <span className="text-lg font-bold text-white">{model.precision_score.toFixed(3)}</span>
          <div className="w-full bg-[#162035] h-1 rounded-full mt-2 overflow-hidden">
            <div className="bg-[#7c3aed] h-full" style={{ width: getMetricPercentage(model.precision_score) }} />
          </div>
        </div>

        {/* Recall */}
        <div className="bg-[#0a0e1a]/55 p-3 rounded-lg border border-[#1e2d4a]/30">
          <span className="text-[#64748b] text-[10px] block uppercase tracking-wider">Recall</span>
          <span className="text-lg font-bold text-white">{model.recall_score.toFixed(3)}</span>
          <div className="w-full bg-[#162035] h-1 rounded-full mt-2 overflow-hidden">
            <div className="bg-[#eab308] h-full" style={{ width: getMetricPercentage(model.recall_score) }} />
          </div>
        </div>

        {/* ROC-AUC */}
        <div className="bg-[#0a0e1a]/55 p-3 rounded-lg border border-[#1e2d4a]/30">
          <span className="text-[#64748b] text-[10px] block uppercase tracking-wider">ROC AUC</span>
          <span className="text-lg font-bold text-white">{model.roc_auc.toFixed(3)}</span>
          <div className="w-full bg-[#162035] h-1 rounded-full mt-2 overflow-hidden">
            <div className="bg-[#10b981] h-full" style={{ width: getMetricPercentage(model.roc_auc) }} />
          </div>
        </div>
      </div>

      {/* Dataset / Training Dates */}
      <div className="space-y-2 border-t border-[#1e2d4a]/40 pt-4 font-mono text-[10px] text-[#64748b] flex flex-col gap-1.5">
        <div className="flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-[#1e2d4a]" />
          <span>Training Corpus: <strong className="text-[#94a3b8]">{model.dataset_trained_on}</strong></span>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-3.5 h-3.5 text-[#1e2d4a]" />
          <span>Last Rebuilt: <strong className="text-[#94a3b8]">{new Date(model.training_date).toLocaleDateString()}</strong></span>
        </div>
      </div>

      {/* Retrain Action */}
      {onRetrain && (
        <button
          onClick={() => onRetrain(model.model_name)}
          className="mt-5 w-full flex items-center justify-center gap-2 py-2 bg-[#162035] hover:bg-[#1e2d4a] text-xs font-semibold text-white rounded-lg border border-[#1e2d4a] hover:border-[#00d4ff]/40 transition-all font-mono"
        >
          <Play className="w-3.5 h-3.5 text-[#00d4ff]" />
          Trigger Retraining
        </button>
      )}
    </div>
  );
};
