'use client';

import { getUserDashboard, getUserStreaks } from '@/lib/api';
import {
    ChartBarIcon,
    CheckCircleIcon,
    FireIcon,
    SparklesIcon,
    TrophyIcon,
} from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';

// Temporary hardcoded user ID (in real app, this would come from auth)
const CURRENT_USER_ID = 1;

interface DashboardData {
  user_id: number;
  total_points: number;
  active_programs: number;
  total_check_ins: number;
  current_streaks: number;
  badges_earned: number;
}

interface Streak {
  id: number;
  habit_id: number;
  current_streak: number;
  longest_streak: number;
}

export default function Home() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [streaks, setStreaks] = useState<Streak[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [dashboardData, streaksData] = await Promise.all([
          getUserDashboard(CURRENT_USER_ID),
          getUserStreaks(CURRENT_USER_ID),
        ]);
        setDashboard(dashboardData);
        setStreaks(streaksData);
      } catch (error) {
        console.error('Failed to load dashboard:', error);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const stats = [
    {
      name: 'Pontos Totais',
      value: dashboard?.total_points || 0,
      icon: TrophyIcon,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-700',
    },
    {
      name: 'Sequências Ativas',
      value: dashboard?.current_streaks || 0,
      icon: FireIcon,
      color: 'bg-orange-500',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-700',
    },
    {
      name: 'Check-ins Totais',
      value: dashboard?.total_check_ins || 0,
      icon: CheckCircleIcon,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-700',
    },
    {
      name: 'Badges Conquistados',
      value: dashboard?.badges_earned || 0,
      icon: SparklesIcon,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-700',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Bem-vindo de volta! Aqui está seu progresso de hoje.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="stat-card">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`${stat.bgColor} p-3 rounded-lg`}>
                  <Icon className={`h-6 w-6 ${stat.textColor}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Streaks */}
      {streaks.length > 0 && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <FireIcon className="h-6 w-6 text-orange-500" />
            <h2 className="text-xl font-bold text-gray-900">Suas Sequências</h2>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {streaks.map((streak) => (
              <div
                key={streak.id}
                className="bg-gradient-to-br from-orange-50 to-red-50 rounded-lg p-4 border border-orange-200"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Sequência Atual</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {streak.current_streak} dias
                    </p>
                  </div>
                  <FireIcon className="h-8 w-8 text-orange-500" />
                </div>
                <div className="mt-2 pt-2 border-t border-orange-200">
                  <p className="text-xs text-gray-600">
                    Recorde: {streak.longest_streak} dias
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Ações Rápidas</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <a
            href="/check-ins"
            className="flex items-center justify-center space-x-3 p-4 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors border border-primary-200"
          >
            <CheckCircleIcon className="h-6 w-6 text-primary-600" />
            <span className="font-medium text-primary-700">Fazer Check-in</span>
          </a>
          <a
            href="/programs"
            className="flex items-center justify-center space-x-3 p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors border border-blue-200"
          >
            <ChartBarIcon className="h-6 w-6 text-blue-600" />
            <span className="font-medium text-blue-700">Ver Programas</span>
          </a>
          <a
            href="/badges"
            className="flex items-center justify-center space-x-3 p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors border border-purple-200"
          >
            <TrophyIcon className="h-6 w-6 text-purple-600" />
            <span className="font-medium text-purple-700">Meus Badges</span>
          </a>
        </div>
      </div>
    </div>
  );
}
