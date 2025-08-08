import { API_BASE_URL } from '@/config/api.config';

export const getRoles = async () => {
  const res = await fetch(`${API_BASE_URL}/role`, {
    method: 'GET',
  });

  if (!res.ok) {
    throw new Error();
  }

  return res.json();
};
