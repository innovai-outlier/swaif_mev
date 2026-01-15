'use client';

import { getUserStreaks } from '@/lib/api';
import { CalendarIcon, FireIcon } from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';

const CURRENT_USER_ID = 1;

interface Streak {
  id: number;
  user_id: number;
  habit_id?: number;
  program_id?: number;
  current_count: number;
  longest_count: number;
  last_activity_date: string;
  habit?: {
    name: string;
    description: string;
  };
  program?: {
    name: string;
    description: string;
  };
}

export default function StreaksPage() {
  const [streaks, setStreaks] = useState<Streak[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStreaks() {
      try {
        const data = await getUserStreaks(CURRENT_USER_ID);
        setStreaks(data);
      } catch (error) {
        console.error('Failed to load streaks:', error);
      } finally {
        setLoading(false);
      }
    }
    loadStreaks();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const activeStreaks = streaks.filter((s) => s.current_count > 0);
  const totalDays = streaks.reduce((sum, s) => sum + s.current_count, 0);
  const longestEver = Math.max(...streaks.map((s) => s.longest_count), 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Sequências</h1>
        <p className="mt-2 text-gray-600">
          Acompanhe suas sequências de hábitos e programas
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="stat-card bg-gradient-to-br from-orange-50 to-red-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sequências Ativas</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {activeStreaks.length}
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
              <FireIcon className="h-7 w-7 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="stat-card bg-gradient-to-br from-yellow-50 to-amber-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total de Dias</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">{totalDays}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <CalendarIcon className="h-7 w-7 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="stat-card bg-gradient-to-br from-purple-50 to-pink-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Recorde Pessoal</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">{longestEver}</p>
              <p className="text-xs text-gray-500">dias consecutivos</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <FireIcon className="h-7 w-7 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Active Streaks */}
      {activeStreaks.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Sequências Ativas 🔥
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {activeStreaks.map((streak) => (
              <div
                key={streak.id}
                className="card bg-gradient-to-br from-orange-50 to-red-50 border-2 border-orange-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900">
                      {streak.habit?.name || streak.program?.name || 'Sequência'}
                    </h3>
                    <p className="mt-1 text-sm text-gray-600">
                      {streak.habit?.description ||
                        streak.program?.description ||
                        ''}
                    </p>
                    <div className="mt-3 flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <FireIcon className="h-5 w-5 text-orange-600" />
                        <div>
                          <p className="text-2xl font-bold text-orange-600">
                            {streak.current_count}
                          </p>
                          <p className="text-xs text-gray-500">dias atuais</p>
                        </div>
                      </div>
                      <div className="border-l border-gray-300 h-12"></div>
                      <div>
                        <p className="text-lg font-semibold text-gray-700">
                          {streak.longest_count}
                        </p>
                        <p className="text-xs text-gray-500">recorde</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-orange-200">
                  <p className="text-xs text-gray-500">
                    Última atividade:{' '}
                    {new Date(streak.last_activity_date).toLocaleDateString(
                      'pt-BR'
                    )}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Streaks */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Todas as Sequências
        </h2>
        <div className="card">
          <div className="space-y-3">
            {streaks.map((streak) => (
              <div
                key={streak.id}
                className={`
                  flex items-center justify-between p-4 rounded-lg transition-colors
                  ${
                    streak.current_count > 0
                      ? 'bg-orange-50 hover:bg-orange-100'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }
                `}
              >
                <div className="flex items-center space-x-3 flex-1">
                  <div
                    className={`
                      w-10 h-10 rounded-full flex items-center justify-center
                      ${
                        streak.current_count > 0
                          ? 'bg-orange-100'
                          : 'bg-gray-200'
                      }
                    `}
                  >
                    <FireIcon
                      className={`h-5 w-5 ${
                        streak.current_count > 0
                          ? 'text-orange-600'
                          : 'text-gray-400'
                      }`}
                    />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {streak.habit?.name || streak.program?.name || 'Sequência'}
                    </p>
                    <p className="text-sm text-gray-500">
                      Atual: {streak.current_count} dias • Recorde:{' '}
                      {streak.longest_count} dias
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    {new Date(streak.last_activity_date).toLocaleDateString(
                      'pt-BR'
                    )}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {streaks.length === 0 && (
        <div className="card bg-gray-50 text-center py-12">
          <FireIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">
            Nenhuma sequência ainda
          </h3>
          <p className="mt-2 text-gray-600">
            Comece a fazer check-ins para iniciar suas sequências!
          </p>
        </div>
      )}
    </div>
  );
}
