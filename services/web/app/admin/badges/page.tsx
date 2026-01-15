"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Badge {
  id: number;
  name: string;
  description: string | null;
  icon: string | null;
  criteria: string | null;
  points_reward: number;
}

export default function AdminBadgesPage() {
  const [badges, setBadges] = useState<Badge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingBadge, setEditingBadge] = useState<Badge | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    icon: "🏆",
    criteria: "",
    points_reward: 10,
  });
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

    fetchBadges(token);
  }, [router]);

  const fetchBadges = async (token: string) => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/admin/badges/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to fetch badges");

      const data = await response.json();
      setBadges(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load badges");
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (badge?: Badge) => {
    if (badge) {
      setEditingBadge(badge);
      setFormData({
        name: badge.name,
        description: badge.description || "",
        icon: badge.icon || "🏆",
        criteria: badge.criteria || "",
        points_reward: badge.points_reward,
      });
    } else {
      setEditingBadge(null);
      setFormData({
        name: "",
        description: "",
        icon: "🏆",
        criteria: "",
        points_reward: 10,
      });
    }
    setShowModal(true);
    setError("");
    setSuccess("");
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingBadge(null);
  };

  const handleSave = async () => {
    setError("");
    setSuccess("");

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authentication token");

      const url = editingBadge
        ? `http://localhost:8000/api/v1/admin/badges/${editingBadge.id}`
        : "http://localhost:8000/api/v1/admin/badges/";

      const method = editingBadge ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to save badge");
      }

      setSuccess(editingBadge ? "Badge atualizado!" : "Badge criado!");
      handleCloseModal();
      fetchBadges(token);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save badge");
    }
  };

  const handleDelete = async (badgeId: number, badgeName: string) => {
    if (!confirm(`Tem certeza que deseja excluir o badge "${badgeName}"?`)) return;

    setError("");
    setSuccess("");

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authentication token");

      const response = await fetch(`http://localhost:8000/api/v1/admin/badges/${badgeId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to delete badge");
      }

      setSuccess("Badge excluído com sucesso!");
      fetchBadges(token);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete badge");
    }
  };

  const commonIcons = ["🏆", "⭐", "🎯", "💪", "🔥", "✨", "🌟", "👑", "💎", "🎖️", "🥇", "🥈", "🥉"];

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
              <h1 className="text-3xl font-bold text-gray-900">Gerenciar Badges</h1>
            </div>
            <button
              onClick={() => handleOpenModal()}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Novo Badge
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
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

          {/* Badges Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {badges.map((badge) => (
              <div key={badge.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-4xl">{badge.icon}</span>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{badge.name}</h3>
                        <p className="text-sm text-gray-600">{badge.description}</p>
                      </div>
                    </div>
                  </div>

                  {badge.criteria && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-xs text-gray-500 font-medium">Critério:</p>
                      <p className="text-sm text-gray-700">{badge.criteria}</p>
                    </div>
                  )}

                  <div className="mt-4 flex items-center justify-between">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                      {badge.points_reward} pts
                    </span>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleOpenModal(badge)}
                        className="text-blue-600 hover:text-blue-800 p-2"
                        title="Editar"
                      >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDelete(badge.id, badge.name)}
                        className="text-red-600 hover:text-red-800 p-2"
                        title="Excluir"
                      >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {badges.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">Nenhum badge cadastrado. Crie o primeiro!</p>
            </div>
          )}
        </div>
      </main>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingBadge ? "Editar Badge" : "Novo Badge"}
              </h2>
            </div>

            <div className="px-6 py-4 space-y-4">
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nome *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: Iniciante"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Descrição</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: Completou o primeiro check-in"
                  rows={2}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Ícone</label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {commonIcons.map((icon) => (
                    <button
                      key={icon}
                      onClick={() => setFormData({ ...formData, icon })}
                      className={`text-2xl p-2 rounded border-2 ${
                        formData.icon === icon ? "border-blue-500 bg-blue-50" : "border-gray-200"
                      }`}
                    >
                      {icon}
                    </button>
                  ))}
                </div>
                <input
                  type="text"
                  value={formData.icon}
                  onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ou digite um emoji personalizado"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Critério de Desbloqueio</label>
                <input
                  type="text"
                  value={formData.criteria}
                  onChange={(e) => setFormData({ ...formData, criteria: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ex: 7 dias consecutivos de check-in"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Pontos de Recompensa</label>
                <input
                  type="number"
                  value={formData.points_reward}
                  onChange={(e) => setFormData({ ...formData, points_reward: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0"
                />
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={handleCloseModal}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                disabled={!formData.name}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {editingBadge ? "Atualizar" : "Criar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
