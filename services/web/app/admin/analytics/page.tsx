'use client';

import AdminHeader from '@/components/AdminHeader';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface AnalyticsOverview {
  overview: {
    total_patients: number;
    total_programs: number;
    active_programs: number;
    total_checkins: number;
    total_points_awarded: number;
    total_enrollments: number;
    total_badges_awarded: number;
  };
  recent_activity: {
    checkins_last_7_days: number;
    checkins_last_30_days: number;
    avg_engagement_rate: number;
  };
  top_performers: {
    most_active_users: Array<{
      user_id: number;
      full_name: string;
      checkin_count: number;
    }>;
    most_popular_programs: Array<{
      program_id: number;
      program_name: string;
      enrollment_count: number;
    }>;
  };
}

interface ProgramPerformance {
  programs: Array<{
    program_id: number;
    program_name: string;
    enrollment_count: number;
    total_checkins: number;
    total_points_awarded: number;
    avg_checkins_per_enrollment: number;
  }>;
}

interface BadgeStatistics {
  total_badges_defined: number;
  total_badges_awarded: number;
  badge_details: Array<{
    badge_id: number;
    badge_name: string;
    description: string;
    points_reward: number;
    times_awarded: number;
  }>;
}

export default function AdminAnalyticsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [programPerformance, setProgramPerformance] = useState<ProgramPerformance | null>(null);
  const [badgeStats, setBadgeStats] = useState<BadgeStatistics | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };

      // Fetch all analytics endpoints
      const [overviewRes, programsRes, badgesRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/admin/analytics/overview', { headers }),
        fetch('http://localhost:8000/api/v1/admin/analytics/program-performance', { headers }),
        fetch('http://localhost:8000/api/v1/admin/analytics/badge-statistics', { headers }),
      ]);

      if (!overviewRes.ok || !programsRes.ok || !badgesRes.ok) {
        throw new Error('Failed to fetch analytics');
      }

      const [overviewData, programsData, badgesData] = await Promise.all([
        overviewRes.json(),
        programsRes.json(),
        badgesRes.json(),
      ]);

      setOverview(overviewData);
      setProgramPerformance(programsData);
      setBadgeStats(badgesData);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Falha ao carregar analytics. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <PageLoading message="Carregando analytics..." />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AdminHeader />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <ErrorAlert message={error} onDismiss={() => setError('')} />
          <button
            onClick={fetchAnalytics}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Tentar Novamente
          </button>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminHeader />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics do Sistema</h1>
          <p className="mt-2 text-gray-600">Métricas e insights de engajamento da plataforma</p>
        </div>

        {/* Overview Cards */}
        {overview && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Total de Pacientes"
              value={overview.overview.total_patients}
              color="blue"
            />

            <StatCard
              title="Programas Ativos"
              value={overview.overview.active_programs}
              subtitle={`de ${overview.overview.total_programs} total`}
              color="green"
            />

            <StatCard
              title="Total de Check-ins"
              value={overview.overview.total_checkins.toLocaleString()}
              color="purple"
            />

            <StatCard
              title="Pontos Distribuídos"
              value={overview.overview.total_points_awarded.toLocaleString()}
              color="yellow"
            />

            <StatCard
              title="Inscrições Ativas"
              value={overview.overview.total_enrollments}
              color="indigo"
            />

            <StatCard
              title="Badges Conquistados"
              value={overview.overview.total_badges_awarded}
              color="pink"
            />

            <StatCard
              title="Check-ins (7 dias)"
              value={overview.recent_activity.checkins_last_7_days}
              color="teal"
            />

            <StatCard
              title="Taxa de Engajamento"
              value={`${overview.recent_activity.avg_engagement_rate}%`}
              subtitle="média semanal"
              color="orange"
            />
          </div>
        )}

        {/* Top Performers Section */}
        {overview && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Most Active Users */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  👤 Usuários Mais Ativos (30 dias)
                </h2>
              </div>
              <div className="p-6">
                {overview.top_performers.most_active_users.length === 0 ? (
                  <p className="text-gray-500 text-center">Nenhum dado disponível</p>
                ) : (
                  <div className="space-y-3">
                    {overview.top_performers.most_active_users.map((user, index) => (
                      <div key={user.user_id} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <span className="text-lg font-bold text-gray-400 w-6">
                            {index + 1}
                          </span>
                          <span className="ml-3 text-gray-900">{user.full_name}</span>
                        </div>
                        <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                          {user.checkin_count} check-ins
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Most Popular Programs */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  🎯 Programas Mais Populares
                </h2>
              </div>
              <div className="p-6">
                {overview.top_performers.most_popular_programs.length === 0 ? (
                  <p className="text-gray-500 text-center">Nenhum dado disponível</p>
                ) : (
                  <div className="space-y-3">
                    {overview.top_performers.most_popular_programs.map((program, index) => (
                      <div key={program.program_id} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <span className="text-lg font-bold text-gray-400 w-6">
                            {index + 1}
                          </span>
                          <span className="ml-3 text-gray-900">{program.program_name}</span>
                        </div>
                        <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                          {program.enrollment_count} inscrições
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Program Performance Table */}
        {programPerformance && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                📊 Performance dos Programas
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Programa
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                      Inscrições
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                      Check-ins
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                      Pontos
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                      Média Check-ins
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {programPerformance.programs.map((program) => (
                    <tr key={program.program_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {program.program_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                        {program.enrollment_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                        {program.total_checkins}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                        {program.total_points_awarded.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                        {program.avg_checkins_per_enrollment}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Badge Statistics */}
        {badgeStats && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                🏆 Estatísticas de Badges
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {badgeStats.total_badges_awarded} badges distribuídos de {badgeStats.total_badges_defined} disponíveis
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Badge
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Descrição
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                      Pontos
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                      Vezes Conquistado
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {badgeStats.badge_details.map((badge) => (
                    <tr key={badge.badge_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {badge.badge_name}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {badge.description}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                        {badge.points_reward}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                        <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium">
                          {badge.times_awarded}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
