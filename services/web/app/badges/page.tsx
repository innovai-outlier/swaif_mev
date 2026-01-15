'use client';

import { getBadges, getUserBadges } from '@/lib/api';
import { CheckBadgeIcon, LockClosedIcon, TrophyIcon } from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';

const CURRENT_USER_ID = 1;

interface Badge {
  id: number;
  name: string;
  description: string;
  icon_url?: string;
  points_reward: number;
}

interface UserBadge {
  id: number;
  badge_id: number;
  awarded_at: string;
  badge: Badge;
}

export default function BadgesPage() {
  const [allBadges, setAllBadges] = useState<Badge[]>([]);
  const [userBadges, setUserBadges] = useState<UserBadge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [badges, earned] = await Promise.all([
          getBadges(),
          getUserBadges(CURRENT_USER_ID),
        ]);
        setAllBadges(badges);
        setUserBadges(earned);
      } catch (error) {
        console.error('Failed to load badges:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const isEarned = (badgeId: number) => {
    return userBadges.some((ub) => ub.badge_id === badgeId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const earnedCount = userBadges.length;
  const totalCount = allBadges.length;
  const completionRate = totalCount > 0 ? Math.round((earnedCount / totalCount) * 100) : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Emblemas</h1>
        <p className="mt-2 text-gray-600">
          Conquiste emblemas completando desafios e marcos
        </p>
      </div>

      {/* Progress Summary */}
      <div className="card bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Emblemas Conquistados</p>
            <p className="mt-1 text-3xl font-bold text-gray-900">
              {earnedCount} / {totalCount}
            </p>
            <p className="mt-1 text-sm text-gray-600">
              {completionRate}% completo
            </p>
          </div>
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg">
            <TrophyIcon className="h-10 w-10 text-yellow-500" />
          </div>
        </div>
        <div className="mt-4 bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-purple-500 to-pink-500 h-full transition-all duration-500"
            style={{ width: `${completionRate}%` }}
          ></div>
        </div>
      </div>

      {/* Earned Badges */}
      {userBadges.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Seus Emblemas</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {userBadges.map((ub) => (
              <div
                key={ub.id}
                className="card bg-gradient-to-br from-yellow-50 to-amber-50 border-2 border-yellow-200"
              >
                <div className="flex items-start space-x-4">
                  <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <CheckBadgeIcon className="h-9 w-9 text-yellow-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900">{ub.badge.name}</h3>
                    <p className="mt-1 text-sm text-gray-600">{ub.badge.description}</p>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="inline-flex items-center px-2 py-1 bg-yellow-100 rounded-full text-xs font-semibold text-yellow-700">
                        +{ub.badge.points_reward} pts
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(ub.awarded_at).toLocaleDateString('pt-BR')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Badges */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Todos os Emblemas</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {allBadges.map((badge) => {
            const earned = isEarned(badge.id);
            return (
              <div
                key={badge.id}
                className={`
                  card transition-all
                  ${
                    earned
                      ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200'
                      : 'bg-gray-50 opacity-60'
                  }
                `}
              >
                <div className="flex items-start space-x-4">
                  <div
                    className={`
                      w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0
                      ${earned ? 'bg-green-100' : 'bg-gray-200'}
                    `}
                  >
                    {earned ? (
                      <CheckBadgeIcon className="h-9 w-9 text-green-600" />
                    ) : (
                      <LockClosedIcon className="h-9 w-9 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3
                      className={`font-bold ${
                        earned ? 'text-gray-900' : 'text-gray-500'
                      }`}
                    >
                      {badge.name}
                    </h3>
                    <p
                      className={`mt-1 text-sm ${
                        earned ? 'text-gray-600' : 'text-gray-400'
                      }`}
                    >
                      {badge.description}
                    </p>
                    <div className="mt-2">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
                          earned
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-200 text-gray-500'
                        }`}
                      >
                        +{badge.points_reward} pts
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
