const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Request failed')
  }

  return response.status === 204 ? null : response.json()
}

export const api = {
  health: () => request('/health'),

  // Sessions
  getSessions: () => request('/sessions'),
  createSession: (payload) =>
    request('/sessions', { method: 'POST', body: JSON.stringify(payload) }),
  getSession: (id) => request(`/sessions/${id}`),
  deleteSession: (id) => request(`/sessions/${id}`, { method: 'DELETE' }),

  // Products
  getProducts: () => request('/products'),
  getProduct: (id) => request(`/products/${id}`),
  compareProducts: (ids) =>
    request('/products/compare', {
      method: 'POST',
      body: JSON.stringify({ product_ids: ids }),
    }),

  // Recommendations
  whyNot: (productId, message, sessionId = null) =>
    request('/recommendations/why-not', {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        message,
        ...(sessionId ? { session_id: sessionId } : {}),
      }),
    }),

  // Chat
  chat: (payload) =>
    request('/chat', { method: 'POST', body: JSON.stringify(payload) }),

  // Preferences
  getPreferences: () => request('/preferences'),
  updatePreferences: (userId, prefs) =>
    request('/preferences', {
      method: 'PUT',
      body: JSON.stringify({ user_id: userId, preferences: prefs }),
    }),

  // Saved products
  getSavedProducts: () => request('/saved-products'),
  saveProduct: (productId) =>
    request('/saved-products', {
      method: 'POST',
      body: JSON.stringify({ user_id: 'demo-user', product_id: productId }),
    }),
  removeSavedProduct: (productId) =>
    request(`/saved-products/${productId}`, { method: 'DELETE' }),
}
