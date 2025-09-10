import api from './api';

export interface BusinessGoal {
  goal: string;
  business_type: string;
  target_audience: string;
  budget: number;
  timeline: string;
}

export interface Campaign {
  id: string;
  name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  score: number;
  status: string;
}

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const parseGoal = async (goalData: BusinessGoal) => {
  const response = await api.post('/api/parse-goal', goalData);
  return response.data;
};

export const getCampaigns = async () => {
  const response = await api.get('/api/campaigns');
  return response.data;
};

export const createCampaign = async (campaignData: any) => {
  const response = await api.post('/api/campaigns', campaignData);
  return response.data;
};

export const generateAICampaign = async (goalData: BusinessGoal) => {
  const response = await api.post('/api/campaigns/ai-generate', goalData);
  return response.data;
};

export const getCampaign = async (id: string) => {
  const response = await api.get(`/api/campaigns/${id}`);
  return response.data;
};

export const getLeads = async () => {
  const response = await api.get('/api/leads');
  return response.data;
};

export const getLead = async (id: string) => {
  const response = await api.get(`/api/leads/${id}`);
  return response.data;
};

export const getAnalytics = async () => {
  const response = await api.get('/api/analytics');
  return response.data;
};
