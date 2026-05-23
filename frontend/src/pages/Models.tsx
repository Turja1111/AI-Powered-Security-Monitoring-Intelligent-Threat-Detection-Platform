import React, { useEffect, useState } from "react";
import { MLModel } from "../types";
import { modelsApi } from "../services/api";
import { Brain, Star, CheckCircle, BarChart3, TrendingUp, Cpu } from "lucide-react";

export default function ModelsPage() {
  const [models, setModels] = useState<MLModel[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const data = await modelsApi.list();
      setModels(data);
    } catch (err) {
      console.error("Failed to load models list:", err);
      // Setup mock models for UI visualization if DB is blank initially
      setModels([
        {
          id: "1",
          model_name: "isolation_forest",
          version: "1.0.2",
          algorithm: "Isolation Forest",
          f1_score: 0.825,
          precision_score: 0.84,
          recall_score: 0.81,
          roc_auc: 0.86,
          training_date: new Date().toISOString(),
          is_active: true,
          dataset_trained_on: "CICIDS2017",
        },
        {
          id: "2",
          model_name: "xgboost_classifier",
          version: "1.4.1",
          algorithm: "XGBoost",
          f1_score: 0.954,
          precision_score: 0.96,
          recall_score: 0.94,
          roc_auc: 0.98,
          training_date: new Date().toISOString(),
          is_active: true,
          dataset_trained_on: "CICIDS2017",
        },
        {
          id: "3",
          model_name: "lstm_detector",
          version: "1.0.0",
          algorithm: "LSTM Autoencoder",
          f1_score: 0.875,
          precision_score: 0.88,
          recall_score: 0.87,
          roc_auc: 0.91,
          training_date: new Date().toISOString(),
          is_active: false,
          dataset_trained_on: "CICIDS2017-Sequence",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleActivate = async (id: string) => {
    try {
      await modelsApi.activate(id);
      fetchModels();
    } catch (err) {
      console.error("Activation failed:", err);
      // Optimistic offline update for fallback demo
      setModels((prev) =>
        prev.map((m) =>
          m.id === id ? { ...m, is_active: true } : { ...m, is_active: false }
        )
      );
    }
  };

  const activeModel = models.find((m) => m.is_active && m.model_name === "xgboost_classifier") || models[1];

  // Mock SHAP values for visualization
  const shapFeatures = [
    { name: "byte_asymmetry_ratio", importance: 0.28 },
    { name: "failed_connection_ratio", importance: 0.22 },
    { name: "unique_dest_ports", importance: 0.18 },
    { name: "tcp_ratio", importance: 0.12 },
    { name: "avg_duration_ms", importance: 0.08 },
  ];

  return (
    <div className="space-y-6">
      {/* ─────────────────────────── CURRENT ACTIVE LEADER ───────────────── */}
      {activeModel && (
        <div className="glass-card p-6 border-l-4 border-l-cyan-400 bg-gradient-to-r from-cyan-950/10 to-transparent">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-cyan-400 animate-pulse" />
                <span className="text-xs font-semibold text-cyan-400 uppercase tracking-widest">Active Primary Classifier</span>
              </div>
              <h2 className="text-xl font-bold text-slate-100">{activeModel.algorithm} Threat Engine</h2>
              <p className="text-xs text-slate-500 font-mono">
                MLflow Version: v{activeModel.version} | Trained On: {activeModel.dataset_trained_on}
              </p>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-xs font-semibold">
              <CheckCircle className="w-4 h-4" />
              Active Serving
            </div>
          </div>

          {/* Core Metrics Grids */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6 pt-6 border-t border-[#1e2d4a]/50">
            <div>
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">F1 Accuracy</span>
              <span className="text-2xl font-bold text-slate-200 font-mono">{(activeModel.f1_score * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">Precision</span>
              <span className="text-2xl font-bold text-slate-200 font-mono">{(activeModel.precision_score * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">Recall</span>
              <span className="text-2xl font-bold text-slate-200 font-mono">{(activeModel.recall_score * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">ROC AUC</span>
              <span className="text-2xl font-bold text-slate-200 font-mono">{activeModel.roc_auc.toFixed(3)}</span>
            </div>
          </div>
        </div>
      )}

      {/* ─────────────────────────── MODELS REGISTRY LIST ────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* MLflow Registry Database */}
        <div className="glass-card p-6 lg:col-span-2 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 border-b border-[#1e2d4a] pb-3">
            MLflow Model Registry versions
          </h3>
          <div className="space-y-4">
            {models.map((model) => (
              <div
                key={model.id}
                className={`p-4 rounded-xl border flex items-center justify-between ${
                  model.is_active
                    ? "bg-[#162035]/30 border-cyan-500/25"
                    : "bg-[#0f1629] border-[#1e2d4a]"
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-200">{model.algorithm}</span>
                    <span className="text-[10px] font-mono text-slate-500 bg-[#162035] px-1.5 py-0.5 rounded border border-[#1e2d4a]">
                      v{model.version}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    F1 Score: {model.f1_score.toFixed(3)} | AUC: {model.roc_auc.toFixed(3)}
                  </div>
                </div>

                <div>
                  {model.is_active ? (
                    <span className="text-xs text-emerald-400 font-semibold bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg flex items-center gap-1">
                      <Star className="w-3.5 h-3.5 fill-current" />
                      Active
                    </span>
                  ) : (
                    <button
                      onClick={() => handleActivate(model.id)}
                      className="text-xs font-semibold text-slate-300 hover:text-cyan-400 hover:border-cyan-500 border border-[#1e2d4a] bg-[#162035] px-3 py-1.5 rounded-lg transition"
                    >
                      Hot-Swap Model
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Feature Importance (SHAP Explainability) */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-[#1e2d4a] pb-3">
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              XGBoost SHAP Feature Importance
            </h3>
          </div>
          <div className="space-y-4 pt-2">
            {shapFeatures.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">{item.name}</span>
                  <span className="text-cyan-400 font-bold">{(item.importance * 100).toFixed(0)}%</span>
                </div>
                <div className="metric-bar">
                  <div
                    className="metric-bar-fill bg-cyan-400 glow-cyan"
                    style={{ width: `${item.importance * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
