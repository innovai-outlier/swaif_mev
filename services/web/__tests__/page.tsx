// eslint-disable-next-line no-unused-vars
import { ChartBarIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';
import { createEnrollment, getProgramHabits, getPrograms, getReminders, getUserEnrollments } from '../../lib/api';
"use client";
"use client";

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
  const [reminders, setReminders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState<number | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [programsData, enrollmentsData, remindersData] = await Promise.all([
          getPrograms(),
          getUserEnrollments(CURRENT_USER_ID),
          getReminders(CURRENT_USER_ID),
        ]);
        setPrograms(programsData);
        setEnrollments(enrollmentsData);
        setReminders(remindersData);
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
            <div key={program.id} className={`border rounded-lg p-6 transition-shadow ${selectedProgram === program.id ? 'border-primary-500 bg-primary-50 shadow-lg' : 'border-gray-200 bg-white'}`}>
              <button
                onClick={() => setSelectedProgram(program.id)}
                className="w-full text-left"
                aria-label={`Selecionar programa ${program.name}`}
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${selectedProgram === program.id ? 'bg-primary-100' : 'bg-gray-100'}`}>
                    <ChartBarIcon className={`h-6 w-6 ${selectedProgram === program.id ? 'text-primary-600' : 'text-gray-600'}`} aria-hidden="true" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{program.name}</h3>
                    <p className="mt-1 text-sm text-gray-600">{program.description}</p>
                  </div>
                </div>
              </button>
              <div className="mt-4 pt-4 border-t border-gray-200">
                {enrolled ? (
                  <div className="flex items-center space-x-2 text-green-700" aria-live="polite">
                    <CheckCircleIcon className="h-5 w-5" aria-hidden="true" />
                    <span className="text-sm font-semibold">Inscrito ✓</span>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => handleEnroll(program.id)}
                    disabled={isEnrollingThis}
                    className="btn-primary w-full"
                    aria-busy={isEnrollingThis}
                    aria-label={isEnrollingThis ? 'Inscrevendo...' : 'Inscrever-se'}
                  >
                    {isEnrollingThis ? 'Inscrevendo...' : 'Inscrever-se'}
                  </button>
                )}
              </div>
              {/* Reminders Section */}
              {selectedProgram === program.id && (
                <section className="mt-8" aria-label="Lembretes do programa">
                  <h2 className="text-lg font-semibold mb-2">Reminders</h2>
                  {reminders.length === 0 ? (
                    <div className="text-gray-500" role="status">No reminders scheduled.</div>
                  ) : (
                    <ul className="space-y-2">
                      {reminders.map(reminder => (
                        <li key={reminder.id} className="border rounded p-2 flex flex-col bg-yellow-50" aria-label={`Lembrete para hábito ${reminder.habit_id}`}>
                          <span><strong>Habit:</strong> {reminder.habit_id}</span>
                          <span><strong>Scheduled for:</strong> {new Date(reminder.scheduled_for).toLocaleString()}</span>
                          <span><strong>Status:</strong> <span className={reminder.status === 'pending' ? 'text-yellow-700' : 'text-green-700'}>{reminder.status}</span></span>
                          {reminder.message && <span><strong>Message:</strong> {reminder.message}</span>}
                        </li>
                      ))}
                    </ul>
                  )}
                </section>
              )}
            </div>
          );
        })}
      </div>

      {/* Habits List */}
      {selectedProgram && habits.length > 0 && (
        <section className="card" aria-label="Hábitos do programa">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Hábitos do Programa
          </h2>
          <div className="space-y-3">
            {habits.map((habit) => (
              <div
                key={habit.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                aria-label={`Hábito ${habit.name}`}
              >
                <div className="flex items-center space-x-3 flex-1">
                  <CheckCircleIcon className="h-5 w-5 text-green-600 flex-shrink-0" aria-hidden="true" />
                  <div>
                    <p className="font-medium text-gray-900">{habit.name}</p>
                    <p className="text-sm text-gray-600">{habit.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2 px-3 py-1 bg-yellow-200 rounded-full">
                  <span className="text-sm font-semibold text-yellow-800">
                    +{habit.points_per_completion}
                  </span>
                  <span className="text-xs text-yellow-700">pts</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

