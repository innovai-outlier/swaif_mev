// API client for Motor Clínico backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Programs
export async function getPrograms() {
  return fetchAPI('/api/v1/programs/');
}

export async function getProgram(id: number) {
  return fetchAPI(`/api/v1/programs/${id}/`);
}

export async function getProgramHabits(programId: number) {
  return fetchAPI(`/api/v1/programs/${programId}/habits/`);
}

// Habits
export async function getHabits(programId?: number) {
  const params = programId ? `?program_id=${programId}` : '';
  return fetchAPI(`/api/v1/habits/${params}`);
}

// Check-ins
export async function getCheckIns(userId: number, startDate?: string, endDate?: string) {
  let params = `?user_id=${userId}`;
  if (startDate) params += `&start_date=${startDate}`;
  if (endDate) params += `&end_date=${endDate}`;
  return fetchAPI(`/api/v1/check-ins/${params}`);
}

export async function createCheckIn(data: {
  user_id: number;
  habit_id: number;
  check_in_date: string;
  notes?: string;
}) {
  return fetchAPI('/api/v1/check-ins/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Users
export async function getUserDashboard(userId: number) {
  return fetchAPI(`/api/v1/users/${userId}/dashboard/`);
}

export async function getUserPoints(userId: number, programId?: number) {
  const params = programId ? `?program_id=${programId}` : '';
  return fetchAPI(`/api/v1/users/${userId}/points/${params}`);
}

export async function getUserPointsHistory(userId: number, programId?: number) {
  const params = programId ? `?program_id=${programId}` : '';
  return fetchAPI(`/api/v1/users/${userId}/points/history/${params}`);
}

export async function getUserStreaks(userId: number) {
  return fetchAPI(`/api/v1/users/${userId}/streaks/`);
}

export async function getUserBadges(userId: number) {
  return fetchAPI(`/api/v1/users/${userId}/badges/`);
}

// Badges
export async function getBadges() {
  return fetchAPI('/api/v1/badges/');
}

// Enrollments
export async function getUserEnrollments(userId: number) {
  return fetchAPI(`/api/v1/enrollments/?user_id=${userId}`);
}

export async function createEnrollment(data: {
  user_id: number;
  program_id: number;
}) {
  return fetchAPI('/api/v1/enrollments/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function cancelEnrollment(enrollmentId: number) {
  return fetchAPI(`/api/v1/enrollments/${enrollmentId}/`, {
    method: 'DELETE',
  });
}
