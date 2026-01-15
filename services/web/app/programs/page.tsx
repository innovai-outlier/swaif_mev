'use client';

import { createEnrollment, getProgramHabits, getPrograms, getUserEnrollments } from '@/lib/api';
import { ChartBarIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';

const CURRENT_USER_ID = 1;

interface Program {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
}

interface Habit {
  id: number;
  name: string;
  description: string;
  points_per_completion: number;
}

interface Enrollment {
  id: number;
  program_id: number;
  user_id: number;
  is_active: boolean;
}

export default function ProgramsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [selectedProgram, setSelectedProgram] = useState<number | null>(null);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState<number | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [programsData, enrollmentsData] = await Promise.all([
          getPrograms(),
          getUserEnrollments(CURRENT_USER_ID),
        ]);
        setPrograms(programsData);
        setEnrollments(enrollmentsData);
        if (programsData.length > 0) {
          setSelectedProgram(programsData[0].id);
        }
      } catch (error) {
        console.error('Failed to load programs:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    if (selectedProgram) {
      getProgramHabits(selectedProgram).then(setHabits);
    }
  }, [selectedProgram]);

  const isEnrolled = (programId: number) => {
    return enrollments.some(
      (e) => e.program_id === programId && e.is_active
    );
  };

  const handleEnroll = async (programId: number) => {
    if (isEnrolled(programId) || enrolling) return;

    setEnrolling(programId);
    try {
      await createEnrollment({
        user_id: CURRENT_USER_ID,
        program_id: programId,
      });

      // Refresh enrollments
      const enrollmentsData = await getUserEnrollments(CURRENT_USER_ID);
      setEnrollments(enrollmentsData);
    } catch (error) {
      console.error('Failed to enroll:', error);
      alert('Erro ao inscrever no programa. Tente novamente.');
    } finally {
      setEnrolling(null);
    }
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
        <h1 className="text-3xl font-bold text-gray-900">Programas</h1>
        <p className="mt-2 text-gray-600">
          Explore os programas disponíveis e inscreva-se para começar
        </p>
      </div>

      {/* Programs Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {programs.map((program) => {
          const enrolled = isEnrolled(program.id);
          const isEnrollingThis = enrolling === program.id;

          return (
            <div
              key={program.id}
              className={`
                p-6 rounded-lg border-2 transition-all
                ${
                  selectedProgram === program.id
                    ? 'border-primary-500 bg-primary-50 shadow-lg'
                    : 'border-gray-200 bg-white'
                }
              `}
            >
              <button
                onClick={() => setSelectedProgram(program.id)}
                className="w-full text-left"
              >
                <div className="flex items-start space-x-3">
                  <div
                    className={`
                    p-2 rounded-lg
                    ${selectedProgram === program.id ? 'bg-primary-100' : 'bg-gray-100'}
                  `}
                  >
                    <ChartBarIcon
                      className={`h-6 w-6 ${
                        selectedProgram === program.id
                          ? 'text-primary-600'
                          : 'text-gray-600'
                      }`}
                    />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{program.name}</h3>
                    <p className="mt-1 text-sm text-gray-600">{program.description}</p>
                  </div>
                </div>
              </button>

              <div className="mt-4 pt-4 border-t border-gray-200">
                {enrolled ? (
                  <div className="flex items-center space-x-2 text-green-600">
                    <CheckCircleIcon className="h-5 w-5" />
                    <span className="text-sm font-semibold">Inscrito ✓</span>
                  </div>
                ) : (
                  <button
                    onClick={() => handleEnroll(program.id)}
                    disabled={isEnrollingThis}
                    className="btn-primary w-full"
                  >
                    {isEnrollingThis ? 'Inscrevendo...' : 'Inscrever-se'}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Habits List */}
      {selectedProgram && habits.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Hábitos do Programa
          </h2>
          <div className="space-y-3">
            {habits.map((habit) => (
              <div
                key={habit.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-3 flex-1">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-gray-900">{habit.name}</p>
                    <p className="text-sm text-gray-600">{habit.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2 px-3 py-1 bg-yellow-100 rounded-full">
                  <span className="text-sm font-semibold text-yellow-700">
                    +{habit.points_per_completion}
                  </span>
                  <span className="text-xs text-yellow-600">pts</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
