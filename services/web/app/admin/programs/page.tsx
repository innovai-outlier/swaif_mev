"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Habit {
  id?: number;
  name: string;
  description: string;
  points_per_completion: number;
  is_active: boolean;
}

interface Program {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  habits: Habit[];
}

export default function AdminProgramsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingProgram, setEditingProgram] = useState<Program | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    is_active: true,
    habits: [] as Habit[],
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

    fetchPrograms(token);
  }, [router]);

  const fetchPrograms = async (token: string) => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/admin/programs/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to fetch programs");

      const data = await response.json();
      setPrograms(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load programs");
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (program?: Program) => {
    if (program) {
      setEditingProgram(program);
      setFormData({
        name: program.name,
        description: program.description || "",
        is_active: program.is_active,
        habits: program.habits.map((h) => ({ ...h })),
      });
    } else {
      setEditingProgram(null);
      setFormData({
        name: "",
        description: "",
        is_active: true,
        habits: [],
      });
    }
    setShowModal(true);
    setError("");
    setSuccess("");
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingProgram(null);
  };

  const handleAddHabit = () => {
    setFormData({
      ...formData,
      habits: [
        ...formData.habits,
        { name: "", description: "", points_per_completion: 10, is_active: true },
      ],
    });
  };

  const handleRemoveHabit = (index: number) => {
    setFormData({
      ...formData,
      habits: formData.habits.filter((_, i) => i !== index),
    });
  };

  const handleHabitChange = (index: number, field: keyof Habit, value: any) => {
    const newHabits = [...formData.habits];
    newHabits[index] = { ...newHabits[index], [field]: value };
    setFormData({ ...formData, habits: newHabits });
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      setError("Nome do programa é obrigatório");
      return;
    }

    if (formData.habits.length === 0) {
      setError("Adicione pelo menos um hábito");
      return;
    }

    if (formData.habits.some((h) => !h.name.trim())) {
      setError("Todos os hábitos devem ter um nome");
      return;
    }

    setError("");
    setSuccess("");

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authentication token");

      const url = editingProgram
        ? `http://localhost:8000/api/v1/admin/programs/${editingProgram.id}`
        : "http://localhost:8000/api/v1/admin/programs/";

      const method = editingProgram ? "PUT" : "POST";

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
        throw new Error(data.detail || "Failed to save program");
      }

      setSuccess(editingProgram ? "Programa atualizado!" : "Programa criado!");
      handleCloseModal();
      fetchPrograms(token);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save program");
    }
  };

  const handleDelete = async (programId: number, programName: string) => {
    if (!confirm(`Tem certeza que deseja excluir o programa "${programName}"?`)) return;

    setError("");
    setSuccess("");

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No authentication token");

      const response = await fetch(`http://localhost:8000/api/v1/admin/programs/${programId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to delete program");
      }

      setSuccess("Programa excluído com sucesso!");
      fetchPrograms(token);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete program");
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
              <h1 className="text-3xl font-bold text-gray-900">Gerenciar Programas</h1>
            </div>
            <button
              onClick={() => handleOpenModal()}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              + Novo Programa
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

          {/* Programs List */}
          <div className="space-y-4">
            {programs.map((program) => (
              <div key={program.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-xl font-semibold text-gray-900">{program.name}</h3>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${
                            program.is_active
                              ? "bg-green-100 text-green-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {program.is_active ? "Ativo" : "Inativo"}
                        </span>
                      </div>
                      {program.description && (
                        <p className="text-sm text-gray-600 mt-2">{program.description}</p>
                      )}

                      {/* Habits List */}
                      <div className="mt-4 space-y-2">
                        <h4 className="text-sm font-medium text-gray-700">Hábitos ({program.habits.length}):</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {program.habits.map((habit) => (
                            <div
                              key={habit.id}
                              className="flex items-center justify-between bg-gray-50 rounded px-3 py-2"
                            >
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">{habit.name}</p>
                                {habit.description && (
                                  <p className="text-xs text-gray-500">{habit.description}</p>
                                )}
                              </div>
                              <span className="text-xs font-medium text-blue-600 ml-2">
                                {habit.points_per_completion} pts
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handleOpenModal(program)}
                        className="text-blue-600 hover:text-blue-800 p-2"
                        title="Editar"
                      >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDelete(program.id, program.name)}
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

          {programs.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">Nenhum programa cadastrado. Crie o primeiro!</p>
            </div>
          )}
        </div>
      </main>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full my-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingProgram ? "Editar Programa" : "Novo Programa"}
              </h2>
            </div>

            <div className="px-6 py-4 space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
                  {error}
                </div>
              )}

              {/* Program Details */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nome do Programa *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Programa de 30 Dias"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Descrição</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Descrição do programa"
                    rows={2}
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                    Programa ativo
                  </label>
                </div>
              </div>

              {/* Habits Section */}
              <div className="border-t border-gray-200 pt-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Hábitos</h3>
                  <button
                    onClick={handleAddHabit}
                    className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 transition-colors"
                  >
                    + Adicionar Hábito
                  </button>
                </div>

                <div className="space-y-4">
                  {formData.habits.map((habit, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                      <div className="flex items-start justify-between mb-3">
                        <h4 className="text-sm font-medium text-gray-700">Hábito {index + 1}</h4>
                        <button
                          onClick={() => handleRemoveHabit(index)}
                          className="text-red-600 hover:text-red-800"
                          title="Remover hábito"
                        >
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Nome *</label>
                          <input
                            type="text"
                            value={habit.name}
                            onChange={(e) => handleHabitChange(index, "name", e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                            placeholder="Ex: Beber 2L de água"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Descrição</label>
                          <input
                            type="text"
                            value={habit.description}
                            onChange={(e) => handleHabitChange(index, "description", e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                            placeholder="Descrição do hábito"
                          />
                        </div>

                        <div className="flex items-center space-x-4">
                          <div className="flex-1">
                            <label className="block text-xs font-medium text-gray-700 mb-1">Pontos</label>
                            <input
                              type="number"
                              value={habit.points_per_completion}
                              onChange={(e) =>
                                handleHabitChange(index, "points_per_completion", parseInt(e.target.value) || 0)
                              }
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                              min="0"
                            />
                          </div>

                          <div className="flex items-center pt-5">
                            <input
                              type="checkbox"
                              id={`habit_active_${index}`}
                              checked={habit.is_active}
                              onChange={(e) => handleHabitChange(index, "is_active", e.target.checked)}
                              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label htmlFor={`habit_active_${index}`} className="ml-2 text-xs text-gray-900">
                              Ativo
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}

                  {formData.habits.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-4">
                      Nenhum hábito adicionado. Clique em "Adicionar Hábito" para começar.
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3 bg-gray-50">
              <button
                onClick={handleCloseModal}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                disabled={!formData.name || formData.habits.length === 0}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {editingProgram ? "Atualizar" : "Criar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
