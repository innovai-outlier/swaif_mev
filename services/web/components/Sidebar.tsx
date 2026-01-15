'use client';

import {
    ChartBarIcon,
    CheckCircleIcon,
    FireIcon,
    HomeIcon,
    SparklesIcon,
    TrophyIcon,
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Check-ins', href: '/check-ins', icon: CheckCircleIcon },
  { name: 'Programas', href: '/programs', icon: ChartBarIcon },
  { name: 'Badges', href: '/badges', icon: TrophyIcon },
  { name: 'Streaks', href: '/streaks', icon: FireIcon },
  { name: 'Recompensas', href: '/rewards', icon: SparklesIcon },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="flex h-16 items-center px-6 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <TrophyIcon className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900">Motor Clínico</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }
              `}
            >
              <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-primary-600' : 'text-gray-400'}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center text-white font-semibold">
            U1
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">Usuário Demo</p>
            <p className="text-xs text-gray-500 truncate">user@demo.com</p>
          </div>
        </div>
      </div>
    </div>
  );
}
