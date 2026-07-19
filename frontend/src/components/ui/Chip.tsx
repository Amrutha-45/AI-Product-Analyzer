import React from 'react';
import { cn } from '../../lib/utils';

export const Chip: React.FC<React.HTMLAttributes<HTMLSpanElement>> = ({ className, children, ...props }) => {
  return (
    <span
      className={cn(
        'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
        'bg-base-700/50 text-text-secondary border border-base-700 hover:bg-base-700 transition-colors cursor-default',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
