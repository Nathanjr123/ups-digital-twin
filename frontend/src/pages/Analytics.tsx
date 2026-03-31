/**
 * Analytics Page
 * Model performance metrics and analytics
 */

import { useEffect, useState } from 'react';
import { Card } from '@/components/common/Card';
import { predictionService } from '@/services/api';
import type { ModelPerformance } from '@/types/prediction';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Brain, TrendingUp } from 'lucide-react';

export function Analytics() {
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance[]>([]);
  
  useEffect(() => {
    const fetchPerformance = async () => {
      try {
        const response = await predictionService.getModelPerformance();
        setModelPerformance(response.data);
      } catch (error) {
        console.error('Error fetching model performance:', error);
      }
    };
    
    fetchPerformance();
  }, []);
  
  const failurePredictor = modelPerformance.find(m => m.model_name === 'failure_predictor');
  
  // Convert feature importance to chart data
  const featureImportanceData = failurePredictor
    ? Object.entries(failurePredictor.feature_importance)
        .slice(0, 10)
        .map(([name, importance]) => ({
          name: name.replace(/_/g, ' '),
          importance: (importance * 100).toFixed(2),
        }))
    : [];
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">
            ML model performance and insights
          </p>
        </div>
        
        {/* Model Performance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {modelPerformance.map((model) => (
            <Card key={model.model_name}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 capitalize">
                    {model.model_name.replace(/_/g, ' ')}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Trained on {model.samples_trained.toLocaleString()} samples
                  </p>
                </div>
                <Brain className="w-8 h-8 text-primary-500" />
              </div>
              
              {model.accuracy !== undefined && (
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div>
                    <p className="text-sm text-gray-600">Accuracy</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {(model.accuracy * 100).toFixed(1)}%
                    </p>
                  </div>
                  
                  {model.precision !== undefined && (
                    <div>
                      <p className="text-sm text-gray-600">Precision</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {(model.precision * 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                  
                  {model.recall !== undefined && (
                    <div>
                      <p className="text-sm text-gray-600">Recall</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {(model.recall * 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                  
                  {model.f1_score !== undefined && (
                    <div>
                      <p className="text-sm text-gray-600">F1 Score</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {(model.f1_score * 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                </div>
              )}
            </Card>
          ))}
        </div>
        
        {/* Feature Importance Chart */}
        {featureImportanceData.length > 0 && (
          <Card
            header={
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  Feature Importance - Failure Predictor
                </h2>
                <TrendingUp className="w-5 h-5 text-primary-500" />
              </div>
            }
          >
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={featureImportanceData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={150} />
                <Tooltip />
                <Bar dataKey="importance" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
            
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> Feature importance indicates which factors contribute most 
                to failure predictions. Higher values mean the feature has more influence on the model's decisions.
              </p>
            </div>
          </Card>
        )}
        
        {/* Additional Insights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <Card header={<h2 className="text-lg font-semibold text-gray-900">Model Insights</h2>}>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Key Prediction Factors</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Battery State of Charge (SOC) is the strongest predictor</li>
                  <li>• Temperature metrics (battery and inverter) are critical indicators</li>
                  <li>• Thermal stress (combined temperature) shows degradation patterns</li>
                  <li>• Load patterns help identify overload scenarios</li>
                </ul>
              </div>
              
              <div className="pt-4 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Model Performance</h4>
                <p className="text-sm text-gray-600">
                  The failure prediction model achieves {failurePredictor && failurePredictor.accuracy 
                    ? `${(failurePredictor.accuracy * 100).toFixed(0)}%` 
                    : 'high'} accuracy in identifying potential failures 
                  7 days in advance, enabling proactive maintenance scheduling.
                </p>
              </div>
            </div>
          </Card>
          
          <Card header={<h2 className="text-lg font-semibold text-gray-900">Recommendations</h2>}>
            <div className="space-y-4 text-sm text-gray-600">
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Monitor Battery Health</h4>
                <p>Regular battery SOC monitoring is crucial for early failure detection.</p>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Temperature Management</h4>
                <p>Maintain proper cooling systems to prevent thermal-induced failures.</p>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Load Balancing</h4>
                <p>Distribute load evenly across UPS units to prevent overload conditions.</p>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-1">Preventive Maintenance</h4>
                <p>Schedule maintenance based on model predictions rather than fixed intervals.</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
