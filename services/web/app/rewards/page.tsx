'use client';

import { ChartBarIcon, FireIcon, SparklesIcon, TrophyIcon } from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000';

interface LeaderboardEntry {
  user_id: number;
  total_points: number;
  total_check_ins: number;
  active_streaks: number;
  badges_count: number;
  rank: number;
}

export default function RewardsPage() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'points' | 'check_ins' | 'streaks' | 'badges'>('points');

  useEffect(() => {
    async function loadLeaderboard() {
      try {
        // Simulate fetching leaderboard data
        // In production, this would be a real API call
        const mockData: LeaderboardEntry[] = Array.from({ length: 30 }, (_, i) => ({
          user_id: i + 1,
          total_points: Math.floor(Math.random() * 1000) + 100,
          total_check_ins: Math.floor(Math.random() * 100) + 10,
          active_streaks: Math.floor(Math.random() * 5),
          badges_count: Math.floor(Math.random() * 10),
          rank: i + 1,
        }));

        // Sort by selected filter
        const sorted = mockData.sort((a, b) => {
          switch (filter) {
            case 'points':
              return b.total_points - a.total_points;
            case 'check_ins':
              return b.total_check_ins - a.total_check_ins;
            case 'streaks':
              return b.active_streaks - a.active_streaks;
            case 'badges':
              return b.badges_count - a.badges_count;
            default:
              return 0;
          }
        });

        // Update ranks
        sorted.forEach((entry, index) => {
          entry.rank = index + 1;
        });

        setLeaderboard(sorted);
      } catch (error) {
        console.error('Failed to load leaderboard:', error);
      } finally {
        setLoading(false);
      }
    }
    loadLeaderboard();
  }, [filter]);

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white';
    if (rank === 2) return 'bg-gradient-to-r from-gray-300 to-gray-500 text-white';
    if (rank === 3) return 'bg-gradient-to-r from-orange-400 to-orange-600 text-white';
    return 'bg-gray-100 text-gray-700';
  };

  const getRankIcon = (rank: number) => {
    if (rank <= 3) return '🏆';
    if (rank <= 10) return '⭐';
    return '🎯';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Recompensas & Ranking</h1>
        <p className="mt-2 text-gray-600">
          Veja sua posição no ranking e competições com outros participantes
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stat-card bg-gradient-to-br from-yellow-50 to-amber-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sua Posição</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">#1</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <TrophyIcon className="h-7 w-7 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="stat-card bg-gradient-to-br from-blue-50 to-indigo-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total de Pontos</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {leaderboard[0]?.total_points || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <SparklesIcon className="h-7 w-7 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="stat-card bg-gradient-to-br from-green-50 to-emerald-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Check-ins</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {leaderboard[0]?.total_check_ins || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <ChartBarIcon className="h-7 w-7 text-green-600" />
            </div>
          </div>
        </div>

        <div className="stat-card bg-gradient-to-br from-orange-50 to-red-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sequências Ativas</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">
                {leaderboard[0]?.active_streaks || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
              <FireIcon className="h-7 w-7 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <button
            onClick={() => setFilter('points')}
            className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
              filter === 'points'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Pontos
          </button>
          <button
            onClick={() => setFilter('check_ins')}
            className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
              filter === 'check_ins'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Check-ins
          </button>
          <button
            onClick={() => setFilter('streaks')}
            className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
              filter === 'streaks'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Sequências
          </button>
          <button
            onClick={() => setFilter('badges')}
            className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
              filter === 'badges'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Emblemas
          </button>
        </div>

        {/* Leaderboard */}
        <div className="space-y-2">
          {leaderboard.slice(0, 20).map((entry) => (
            <div
              key={entry.user_id}
              className={`
                flex items-center justify-between p-4 rounded-lg transition-colors
                ${
                  entry.rank <= 3
                    ? 'bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-200'
                    : 'bg-gray-50 hover:bg-gray-100'
                }
              `}
            >
              <div className="flex items-center space-x-4">
                <div
                  className={`
                    w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg
                    ${getRankBadgeColor(entry.rank)}
                  `}
                >
                  {entry.rank <= 10 ? getRankIcon(entry.rank) : entry.rank}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">
                    Paciente {entry.user_id}
                    {entry.user_id === 1 && (
                      <span className="ml-2 text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full">
                        Você
                      </span>
                    )}
                  </p>
                  <p className="text-sm text-gray-600">
                    {filter === 'points' && `${entry.total_points} pontos`}
                    {filter === 'check_ins' && `${entry.total_check_ins} check-ins`}
                    {filter === 'streaks' && `${entry.active_streaks} sequências`}
                    {filter === 'badges' && `${entry.badges_count} emblemas`}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="text-center">
                  <p className="font-semibold text-gray-900">{entry.total_points}</p>
                  <p className="text-xs">pts</p>
                </div>
                <div className="text-center">
                  <p className="font-semibold text-gray-900">{entry.total_check_ins}</p>
                  <p className="text-xs">check-ins</p>
                </div>
                <div className="text-center">
                  <p className="font-semibold text-gray-900">{entry.active_streaks}</p>
                  <p className="text-xs">sequências</p>
                </div>
                <div className="text-center">
                  <p className="font-semibold text-gray-900">{entry.badges_count}</p>
                  <p className="text-xs">emblemas</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Motivational Message */}
      <div className="card bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
            <TrophyIcon className="h-8 w-8 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-purple-900">
              Continue assim! 🎉
            </h3>
            <p className="mt-1 text-purple-700">
              Você está entre os melhores! Continue fazendo check-ins diários para
              manter sua posição no ranking.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
