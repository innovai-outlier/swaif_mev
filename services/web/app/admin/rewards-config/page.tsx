"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface RewardConfig {
  config_key: string;
  config_value: number;
  description: string;
}

export default function RewardsConfigPage() {
  const [configs, setConfigs] = useState<RewardConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");

    if (!token || !userData) {
      router.push("/login");
      return;
    }

    const user = JSON.parse(userData);
    if (user.role !== "admin") {
      router.push("/");
      return;
    }

    fetchConfigs(token);
  }, [router]);

  const fetchConfigs = async (token: string) => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/admin/rewards/config", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to fetch configs");

      const data = await response.json();
      setConfigs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load configs");
    } finally {
      setLoading(false);
    }
  };

  const handleValueChange = (configKey: string, newValue: string) => {
    const numValue = parseInt(newValue) || 0;
    setConfigs(
      configs.map((c) => (c.config_key === configKey ? { ...c, config_value: numValue } : c))
    );
  };

  const handleSave = async () => {
    setError("");
    setSuccess("");
    setSaving(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authentication token");

      const response = await fetch("http://localhost:8000/api/v1/admin/rewards/config", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ configs }),
      });

      if (!response.ok) throw new Error("Failed to save configs");

      setSuccess("Configurações salvas com sucesso!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save configs");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Tem certeza que deseja restaurar as configurações padrão?")) return;

    setError("");
    setSuccess("");
    setSaving(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authentication token");

      const response = await fetch("http://localhost:8000/api/v1/admin/rewards/config/reset", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to reset configs");

      const data = await response.json();
      setConfigs(data);
      setSuccess("Configurações restauradas para o padrão!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset configs");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-8">Carregando...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/admin" className="text-gray-500 hover:text-gray-700">
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">Configurar Recompensas</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}

          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-900">Sistema de Pontuação</h2>
              <p className="text-sm text-gray-600 mt-1">
                Configure os valores de pontos para diferentes ações e marcos
              </p>
            </div>

            <div className="divide-y divide-gray-200">
              {configs.map((config) => (
                <div key={config.config_key} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <label htmlFor={config.config_key} className="block text-sm font-medium text-gray-900">
                        {config.description}
                      </label>
                      <p className="text-xs text-gray-500 mt-1">{config.config_key}</p>
                    </div>
                    <div className="ml-4 flex items-center space-x-2">
                      <input
                        type="number"
                        id={config.config_key}
                        value={config.config_value}
                        onChange={(e) => handleValueChange(config.config_key, e.target.value)}
                        className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        min="0"
                      />
                      <span className="text-sm text-gray-600 font-medium">pts</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-6 flex justify-end space-x-4">
            <button
              onClick={handleReset}
              disabled={saving}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Restaurar Padrão
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {saving ? "Salvando..." : "Salvar Alterações"}
            </button>
          </div>

          {/* Info Box */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex">
              <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">Dica</h3>
                <p className="text-sm text-blue-700 mt-1">
                  As configurações de pontos afetarão todas as novas ações dos pacientes. 
                  Alterações não afetarão pontos já concedidos anteriormente.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
