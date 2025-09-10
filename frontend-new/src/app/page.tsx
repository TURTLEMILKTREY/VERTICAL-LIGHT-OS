'use client';

import { useEffect, useState } from 'react';
import { checkHealth, parseGoal, getCampaigns, getLeads, getAnalytics, createCampaign } from '@/lib/services';

interface Analytics {
  total_campaigns: number;
  active_campaigns: number;
  total_leads: number;
  conversion_rate: number;
  total_spend: number;
  total_revenue: number;
  roi: number;
}

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [campaigns, setCampaigns] = useState([]);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Check backend connection
        await checkHealth();
        setIsConnected(true);

        // Load dashboard data
        const [analyticsData, campaignsData, leadsData] = await Promise.all([
          getAnalytics(),
          getCampaigns(),
          getLeads()
        ]);

        setAnalytics(analyticsData);
        setCampaigns(campaignsData);
        setLeads(leadsData);
      } catch (error) {
        console.error('Failed to load data:', error);
        setIsConnected(false);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleCreateTestCampaign = async () => {
    try {
      const testCampaign = {
        name: 'Test Campaign',
        goal: 'Increase brand awareness',
        budget: 1000,
        target_audience: 'Young professionals',
        channels: ['Google Ads', 'Facebook Ads']
      };
      
      await createCampaign(testCampaign);
      // Reload campaigns
      const campaignsData = await getCampaigns();
      setCampaigns(campaignsData);
    } catch (error) {
      console.error('Failed to create campaign:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">VERTICAL LIGHT OS</h1>
          <p className="text-gray-600">AI-Powered Marketing Platform</p>
          
          {/* Connection Status */}
          <div className="mt-4 flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className={`text-sm ${isConnected ? 'text-green-700' : 'text-red-700'}`}>
              Backend {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {!isConnected ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            <strong>Connection Error:</strong> Unable to connect to backend. Make sure the FastAPI server is running on port 8000.
          </div>
        ) : (
          <>
            {/* Analytics Cards */}
            {analytics && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-sm font-medium text-gray-500">Total Campaigns</h3>
                  <p className="text-2xl font-bold text-gray-900">{analytics.total_campaigns}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-sm font-medium text-gray-500">Active Campaigns</h3>
                  <p className="text-2xl font-bold text-green-600">{analytics.active_campaigns}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-sm font-medium text-gray-500">Total Leads</h3>
                  <p className="text-2xl font-bold text-blue-600">{analytics.total_leads}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-sm font-medium text-gray-500">ROI</h3>
                  <p className="text-2xl font-bold text-purple-600">{analytics.roi.toFixed(1)}%</p>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="mb-8 flex flex-wrap gap-4">
              <button
                onClick={handleCreateTestCampaign}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                Create Test Campaign
              </button>
              
              <a
                href="/ai-features"
                className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-md transition-colors inline-block"
              >
                🤖 Try AI Features
              </a>
            </div>

            {/* Campaigns Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Campaigns</h2>
                {campaigns.length > 0 ? (
                  <div className="space-y-3">
                    {campaigns.slice(0, 5).map((campaign: any) => (
                      <div key={campaign.id} className="border-l-4 border-blue-500 pl-4">
                        <h3 className="font-medium text-gray-900">{campaign.name}</h3>
                        <p className="text-sm text-gray-600">Status: {campaign.status}</p>
                        <p className="text-sm text-gray-600">Budget: ${campaign.budget}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No campaigns yet. Create your first campaign to get started!</p>
                )}
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Leads</h2>
                {leads.length > 0 ? (
                  <div className="space-y-3">
                    {leads.slice(0, 5).map((lead: any) => (
                      <div key={lead.id} className="border-l-4 border-green-500 pl-4">
                        <h3 className="font-medium text-gray-900">{lead.name}</h3>
                        <p className="text-sm text-gray-600">{lead.email}</p>
                        <p className="text-sm text-gray-600">Score: {lead.score}/100</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No leads yet. Your campaigns will start generating leads soon!</p>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
