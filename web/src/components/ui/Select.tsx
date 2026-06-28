import type { SelectHTMLAttributes } from 'react';
import { cn } from '../../lib/cn';
import type { FieldOption } from '../../api/types';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: FieldOption[];
  placeholder?: string;
}

export function Select({ className, label, options, placeholder, ...props }: SelectProps) {
  return (
    <div className="form-group">
      {label && <label className="form-label">{label}</label>}
      <select className={cn('select', className)} {...props}>
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
