import axios from './axios';

const BASE_URL = '/optimization-control/';

export const optimizationApi = {
  // Get optimization recommendation
  getOptimizationRecommendation: (startDate, endDate) => {
    return axios.post(`${BASE_URL}`, {
      start: startDate,
      end: endDate,
    });
  },

  // Get optimization with default dates (next 24h)
  getDefaultOptimization: () => {
    return axios.post(`${BASE_URL}`);
  },
};
