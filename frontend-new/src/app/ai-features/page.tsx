'use client';

import { useState } from 'react';
import { parseGoal, generateAICampaign } from '@/lib/services';

interface GoalParseResult {
  parsed_goal: string;
  strategy: string;
  recommended_channels: string[];
  estimated_cost: number;
  success_metrics: string[];
  confidence_score?: number;
  complexity_score?: number;
  urgency_level?: string;
  risk_factors?: string[];
  optimization_opportunities?: string[];
}

export default function AIFeatures() {
  const [goalText, setGoalText] = useState('');
  const [businessType, setBusinessType] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [budget, setBudget] = useState(5000);
  const [timeline, setTimeline] = useState('1 month');
  
  const [parseResult, setParseResult] = useState<GoalParseResult | null>(null);
  const [campaignResult, setCampaignResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleParseGoal = async () => {
    if (!goalText || !businessType || !targetAudience) {
      alert('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const result = await parseGoal({
        goal: goalText,
        business_type: businessType,
        target_audience: targetAudience,
        budget: budget,
        timeline: timeline
      });
      
      setParseResult(result);
    } catch (error) {
      console.error('Failed to parse goal:', error);
      alert('Failed to parse goal. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCampaign = async () => {
    if (!goalText || !businessType || !targetAudience) {
      alert('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const result = await generateAICampaign({
        goal: goalText,
        business_type: businessType,
        target_audience: targetAudience,
        budget: budget,
        timeline: timeline
      });
      
      setCampaignResult(result);
    } catch (error) {
      console.error('Failed to generate campaign:', error);
      alert('Failed to generate campaign. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">🤖 AI Marketing Features</h1>
        
        {/* Input Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Business Goal *
            </label>
            <textarea
              value={goalText}
              onChange={(e) => setGoalText(e.target.value)}
              placeholder="e.g., Increase online sales by 30% this quarter"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Business Type *
            </label>
            <select
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select Business Type</option>
              <option value="e-commerce">E-commerce</option>
              <option value="saas">SaaS</option>
              <option value="local_business">Local Business</option>
              <option value="consulting">Consulting</option>
              <option value="healthcare">Healthcare</option>
              <option value="education">Education</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Audience *
            </label>
            <input
              type="text"
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
              placeholder="e.g., Young professionals aged 25-35"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Budget ($)
            </label>
            <input
              type="number"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Timeline
            </label>
            <select
              value={timeline}
              onChange={(e) => setTimeline(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="2 weeks">2 weeks</option>
              <option value="1 month">1 month</option>
              <option value="2 months">2 months</option>
              <option value="3 months">3 months</option>
              <option value="6 months">6 months</option>
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-4 mb-8">
          <button
            onClick={handleParseGoal}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-md transition-colors"
          >
            {loading ? 'Processing...' : '🎯 Analyze Goal with AI'}
          </button>
          
          <button
            onClick={handleGenerateCampaign}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-md transition-colors"
          >
            {loading ? 'Generating...' : '🚀 Generate AI Campaign'}
          </button>
        </div>

        {/* Results */}
        {parseResult && (
          <div className="bg-blue-50 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-blue-900 mb-4">🎯 AI Goal Analysis</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium text-blue-800 mb-2">Parsed Goal</h3>
                <p className="text-blue-700">{parseResult.parsed_goal}</p>
              </div>
              
              <div>
                <h3 className="font-medium text-blue-800 mb-2">Recommended Channels</h3>
                <div className="flex flex-wrap gap-1">
                  {parseResult.recommended_channels.map((channel, index) => (
                    <span key={index} className="bg-blue-200 text-blue-800 px-2 py-1 rounded text-sm">
                      {channel}
                    </span>
                  ))}
                </div>
              </div>
              
              {parseResult.confidence_score && (
                <div>
                  <h3 className="font-medium text-blue-800 mb-2">AI Confidence</h3>
                  <div className="bg-blue-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${parseResult.confidence_score * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-blue-700 mt-1">{(parseResult.confidence_score * 100).toFixed(1)}%</p>
                </div>
              )}
              
              <div>
                <h3 className="font-medium text-blue-800 mb-2">Success Metrics</h3>
                <ul className="text-blue-700 text-sm">
                  {parseResult.success_metrics.slice(0, 3).map((metric, index) => (
                    <li key={index} className="mb-1">• {metric}</li>
                  ))}
                </ul>
              </div>
            </div>
            
            {parseResult.risk_factors && parseResult.risk_factors.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium text-blue-800 mb-2">⚠️ Risk Factors</h3>
                <ul className="text-blue-700 text-sm">
                  {parseResult.risk_factors.map((risk, index) => (
                    <li key={index} className="mb-1">• {risk}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {campaignResult && (
          <div className="bg-green-50 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-green-900 mb-4">🚀 AI-Generated Campaign</h2>
            
            {campaignResult.ai_details && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-medium text-green-800 mb-2">Campaign Details</h3>
                  <p><strong>Name:</strong> {campaignResult.ai_details.name}</p>
                  <p><strong>Objective:</strong> {campaignResult.ai_details.objective}</p>
                  <p><strong>Budget:</strong> ${campaignResult.ai_details.budget}</p>
                  <p><strong>Timeline:</strong> {campaignResult.ai_details.timeline}</p>
                </div>
                
                <div>
                  <h3 className="font-medium text-green-800 mb-2">AI Insights</h3>
                  {campaignResult.ai_details.ai_insights && (
                    <div>
                      <p><strong>Confidence:</strong> {(campaignResult.ai_details.ai_insights.confidence_score * 100).toFixed(1)}%</p>
                      <p><strong>Complexity:</strong> {(campaignResult.ai_details.ai_insights.complexity_score * 100).toFixed(1)}%</p>
                      {campaignResult.ai_details.ai_insights.predicted_performance && (
                        <p><strong>Est. Clicks:</strong> {campaignResult.ai_details.ai_insights.predicted_performance.estimated_clicks}</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            <div className="mt-4">
              <p className="text-green-700 font-medium">{campaignResult.message}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
