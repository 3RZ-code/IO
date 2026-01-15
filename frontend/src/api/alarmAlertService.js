import api from './axios';

// ==================== ALERTS ====================

/**
 * Pobierz wszystkie alerty (z opcjonalnymi filtrami)
 * @param {Object} filters - { severity, status, category }
 */
export const getAlerts = async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.status) params.append('status', filters.status);
    if (filters.category) params.append('category', filters.category);
    
    const response = await api.get(`/alarm-alert/alerts/?${params.toString()}`);
    return response.data;
};

/**
 * Pobierz szczegóły pojedynczego alertu
 */
export const getAlertById = async (alertId) => {
    const response = await api.get(`/alarm-alert/alerts/${alertId}/`);
    return response.data;
};

/**
 * Utwórz nowy alert (tylko admin)
 */
export const createAlert = async (alertData) => {
    const response = await api.post('/alarm-alert/alerts/', alertData);
    return response.data;
};

/**
 * Aktualizuj alert (tylko admin)
 */
export const updateAlert = async (alertId, alertData) => {
    const response = await api.put(`/alarm-alert/alerts/${alertId}/`, alertData);
    return response.data;
};

/**
 * Usuń alert (tylko admin)
 */
export const deleteAlert = async (alertId) => {
    const response = await api.delete(`/alarm-alert/alerts/${alertId}/`);
    return response.data;
};

/**
 * Potwierdź alert
 */
export const confirmAlert = async (alertId) => {
    const response = await api.post(`/alarm-alert/alerts/${alertId}/confirm/`);
    return response.data;
};

/**
 * Wycisz alert
 */
export const muteAlert = async (alertId) => {
    const response = await api.post(`/alarm-alert/alerts/${alertId}/mute/`);
    return response.data;
};

/**
 * Pobierz moje alerty (użytkownika)
 */
export const getMyAlerts = async () => {
    const response = await api.get('/alarm-alert/alerts/my_alerts/');
    return response.data;
};

/**
 * Pobierz statystyki alertów
 */
export const getAlertStatistics = async () => {
    const response = await api.get('/alarm-alert/alerts/statistics/');
    return response.data;
};

// ==================== NOTIFICATIONS ====================

/**
 * Pobierz wszystkie powiadomienia
 * @param {boolean} isRead - filtruj po statusie przeczytania
 */
export const getNotifications = async (isRead = null) => {
    const params = isRead !== null ? `?is_read=${isRead}` : '';
    const response = await api.get(`/alarm-alert/notifications/${params}`);
    return response.data;
};

/**
 * Pobierz szczegóły powiadomienia
 */
export const getNotificationById = async (notificationId) => {
    const response = await api.get(`/alarm-alert/notifications/${notificationId}/`);
    return response.data;
};

/**
 * Oznacz powiadomienie jako przeczytane
 */
export const markNotificationAsRead = async (notificationId) => {
    const response = await api.post(`/alarm-alert/notifications/${notificationId}/mark_as_read/`);
    return response.data;
};

/**
 * Oznacz wszystkie powiadomienia jako przeczytane
 */
export const markAllNotificationsAsRead = async () => {
    const response = await api.post('/alarm-alert/notifications/mark_all_as_read/');
    return response.data;
};

/**
 * Pobierz liczbę nieprzeczytanych powiadomień
 */
export const getUnreadNotificationsCount = async () => {
    const response = await api.get('/alarm-alert/notifications/unread_count/');
    return response.data;
};

// ==================== PREFERENCES ====================

/**
 * Pobierz moje preferencje powiadomień
 */
export const getMyPreferences = async () => {
    const response = await api.get('/alarm-alert/preferences/my_preferences/');
    return response.data;
};

/**
 * Aktualizuj moje preferencje powiadomień
 */
export const updateMyPreferences = async (preferencesData) => {
    const response = await api.put('/alarm-alert/preferences/my_preferences/', preferencesData);
    return response.data;
};

/**
 * Ustaw godziny ciszy (Quiet Hours)
 */
export const setQuietHours = async (preferenceId, startTime, endTime) => {
    const response = await api.post(`/alarm-alert/preferences/${preferenceId}/set_quiet_hours/`, {
        quiet_hours_start: startTime,
        quiet_hours_end: endTime
    });
    return response.data;
};
