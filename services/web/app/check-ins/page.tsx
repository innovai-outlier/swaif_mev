'use client';

import { createCheckIn, getCheckIns, getHabits } from '@/lib/api';
import { CheckCircleIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';
import { useEffect, useState } from 'react';

const CURRENT_USER_ID = 1;

interface Habit {
  id: number;
  name: string;
  description: string;
  points_per_completion: number;
  program_id: number;
  is_active?: boolean;
}

interface CheckIn {
  id: number;
  habit_id: number;
  check_in_date: string;
}

export default function CheckInsPage() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [todayCheckIns, setTodayCheckIns] = useState<CheckIn[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState<number | null>(null);

  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    async function loadData() {
      try {
        const [habitsData, checkInsData] = await Promise.all([
          getHabits(),
          getCheckIns(CURRENT_USER_ID, today, today),
        ]);
        setHabits(habitsData.filter((h: Habit) => h.is_active !== false));
        setTodayCheckIns(checkInsData);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [today]);

  const isCheckedIn = (habitId: number) => {
    return todayCheckIns.some((ci) => ci.habit_id === habitId);
  };

  const handleCheckIn = async (habit: Habit) => {
    if (isCheckedIn(habit.id) || submitting) return;

    setSubmitting(habit.id);
    try {
      await createCheckIn({
        user_id: CURRENT_USER_ID,
        habit_id: habit.id,
        check_in_date: today,
        notes: `Check-in automático - ${new Date().toLocaleTimeString('pt-BR')}`,
      });

      // Refresh check-ins
      const checkInsData = await getCheckIns(CURRENT_USER_ID, today, today);
      setTodayCheckIns(checkInsData);
    } catch (error) {
      console.error('Failed to create check-in:', error);
      alert('Erro ao fazer check-in. Tente novamente.');
    } finally {
      setSubmitting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const completedToday = todayCheckIns.length;
  const totalHabits = habits.length;
  const completionRate = totalHabits > 0 ? Math.round((completedToday / totalHabits) * 100) : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Check-ins Diários</h1>
        <p className="mt-2 text-gray-600">
          Registre seus hábitos e ganhe pontos!
        </p>
      </div>

      {/* Progress Summary */}
      <div className="card bg-gradient-to-br from-primary-50 to-blue-50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Progresso de Hoje</p>
            <p className="mt-1 text-3xl font-bold text-gray-900">
              {completedToday} / {totalHabits}
            </p>
            <p className="mt-1 text-sm text-gray-600">
              {completionRate}% completo
            </p>
          </div>
          <div className="text-right">
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow">
              <SparklesIcon className="h-5 w-5 text-yellow-500" />
              <span className="text-sm font-semibold text-gray-900">
                Ganhe até {habits.reduce((sum, h) => sum + h.points_per_completion, 0)} pontos hoje!
              </span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4 bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-primary-500 to-primary-600 h-full transition-all duration-500"
            style={{ width: `${completionRate}%` }}
          ></div>
        </div>
      </div>

      {/* Habits List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {habits.map((habit) => {
          const checked = isCheckedIn(habit.id);
          const isSubmittingThis = submitting === habit.id;

          return (
            <button
              key={habit.id}
              onClick={() => handleCheckIn(habit)}
              disabled={checked || isSubmittingThis}
              className={`
                text-left p-6 rounded-lg border-2 transition-all
                ${
                  checked
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-white hover:border-primary-300 hover:shadow-md'
                }
                ${(checked || isSubmittingThis) ? 'cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className="flex items-start space-x-4">
                <div className={`
                  flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center
                  ${checked ? 'bg-green-100' : 'bg-gray-100'}
                `}>
                  {checked ? (
                    <CheckCircleSolid className="h-7 w-7 text-green-600" />
                  ) : (
                    <CheckCircleIcon className="h-7 w-7 text-gray-400" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <h3 className="font-semibold text-gray-900">{habit.name}</h3>
                    <span className={`
                      ml-2 px-2 py-1 rounded-full text-xs font-semibold
                      ${checked ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}
                    `}>
                      +{habit.points_per_completion} pts
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-600">{habit.description}</p>
                  {checked && (
                    <p className="mt-2 text-sm font-medium text-green-600">
                      ✓ Completado hoje!
                    </p>
                  )}
                  {isSubmittingThis && (
                    <p className="mt-2 text-sm text-primary-600">Registrando...</p>
                  )}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {completionRate === 100 && (
        <div className="card bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <SparklesIcon className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-green-900">
                Parabéns! Você completou todos os hábitos de hoje! 🎉
              </h3>
              <p className="text-sm text-green-700">Continue assim para manter suas sequências!</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
