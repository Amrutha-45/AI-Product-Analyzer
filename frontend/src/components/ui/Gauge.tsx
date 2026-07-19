import React from 'react';
import { cn } from '../../lib/utils';

interface GaugeProps {
  value: number; // 0 to 100
  size?: number;
  strokeWidth?: number;
  label?: string;
  colorClass?: string;
  className?: string;
}

export const Gauge: React.FC<GaugeProps> = ({
  value,
  size = 120,
  strokeWidth = 10,
  label,
  colorClass = 'text-primary',
  className,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (value / 100) * circumference;

  // Determine dynamic color if none explicitly provided
  const dynamicColorClass = React.useMemo(() => {
    if (colorClass !== 'text-primary') return colorClass;
    if (value >= 80) return 'text-accent'; // Green
    if (value >= 50) return 'text-accent-warning'; // Yellow
    return 'text-accent-danger'; // Red
  }, [value, colorClass]);

  return (
    <div className={cn("relative flex flex-col items-center justify-center", className)} style={{ width: size, height: size }}>
      <svg className="transform -rotate-90 w-full h-full">
        {/* Background Circle */}
        <circle
          className="text-base-700"
          strokeWidth={strokeWidth}
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        {/* Foreground Circle */}
        <circle
          className={cn("transition-all duration-1000 ease-out", dynamicColorClass)}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-3xl font-bold text-white">{value}</span>
        {label && <span className="text-xs text-text-secondary uppercase tracking-wider">{label}</span>}
      </div>
    </div>
  );
};
