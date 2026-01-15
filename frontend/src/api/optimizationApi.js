import axios from './axios';

const BASE_URL = '/optimization-control/';

export const optimizationApi = {
  getOptimizationRecommendation: (startDate, endDate) => {
    return axios.post(`${BASE_URL}`, {
      start: startDate,
      end: endDate,
    });
  },

  getDefaultOptimization: () => {
    return axios.post(`${BASE_URL}`);
  },
};
