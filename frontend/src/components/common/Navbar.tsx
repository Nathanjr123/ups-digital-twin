/**
 * Navbar Component
 * Top navigation bar with app branding and navigation links
 */

import { Link, useLocation } from 'react-router-dom';
import { Activity, AlertCircle, BarChart3, Layout, FlaskConical } from 'lucide-react';
import { cn } from '@/utils/formatters';
import { APP_NAME } from '@/utils/constants';

const navigation = [
  { name: 'Overview', href: '/', icon: Layout },
  { name: 'Fleet', href: '/fleet', icon: Activity },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Alerts', href: '/alerts', icon: AlertCircle },
  { name: 'Simulation', href: '/simulation', icon: FlaskConical },
];

export function Navbar() {
  const location = useLocation();
  
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            {/* Logo */}
            <div className="flex-shrink-0 flex items-center">
              <Activity className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                {APP_NAME}
              </span>
            </div>
            
            {/* Navigation Links */}
            <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'inline-flex items-center px-3 py-2 text-sm font-medium rounded-md',
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    )}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
          
          {/* Right side - could add user menu, settings, etc. */}
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-gray-600">Live</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
