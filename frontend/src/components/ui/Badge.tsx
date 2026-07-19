import React from 'react';
import { cn } from '../../lib/utils';

export type RiskLevel = 'safe' | 'moderate' | 'high' | 'unclear';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  level: RiskLevel;
}

export const Badge: React.FC<BadgeProps> = ({ level, className, children, ...props }) => {
  const styles = {
    safe: 'bg-accent-10 text-accent border border-accent/20',
    moderate: 'bg-accent-warning/10 text-accent-warning border border-accent-warning/20',
    high: 'bg-accent-danger/10 text-accent-danger border border-accent-danger/20',
    unclear: 'bg-base-700 text-text-secondary border border-base-700/50',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        styles[level],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
