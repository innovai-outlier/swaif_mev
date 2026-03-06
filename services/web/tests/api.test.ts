import { afterEach, describe, expect, it, vi } from 'vitest';
import { cancelEnrollment, getPrograms } from '../lib/api';

describe('web api client', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('injects bearer token when available', async () => {
    localStorage.setItem('token', 'abc123');
    const fetchMock = vi.spyOn(global, 'fetch' as never).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ id: 1, name: 'P1' }],
    } as Response);

    await getPrograms();

    const [, options] = fetchMock.mock.calls[0];
    expect((options as RequestInit).headers).toMatchObject({
      Authorization: 'Bearer abc123',
    });
  });

  it('returns null on 204 responses', async () => {
    vi.spyOn(global, 'fetch' as never).mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => ({}),
    } as Response);

    const response = await cancelEnrollment(99);
    expect(response).toBeNull();
  });

  it('throws descriptive error on failed response', async () => {
    vi.spyOn(global, 'fetch' as never).mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Bad request payload' }),
    } as Response);

    await expect(getPrograms()).rejects.toThrow('Bad request payload');
  });
});
