import React, { useEffect, useRef } from 'react';

export interface ContextMenuItem {
  label: string;
  icon: string;
  danger?: boolean;
  onClick: () => void;
}

interface ContextMenuProps {
  visible: boolean;
  position: { x: number; y: number };
  items: ContextMenuItem[];
  onClose: () => void;
}

export default function ContextMenu({ visible, position, items, onClose }: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!visible) return;

    const handleClickOutside = (e: MouseEvent | TouchEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [visible, onClose]);

  if (!visible) return null;

  // Clamp position to viewport
  const menuWidth = 200;
  const menuHeight = items.length * 48;
  const x = Math.min(position.x, window.innerWidth - menuWidth - 16);
  const y = Math.min(position.y, window.innerHeight - menuHeight - 16);

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 z-[80] bg-transparent" onClick={onClose} />

      {/* Menu */}
      <div
        ref={menuRef}
        className="fixed z-[90] bg-white rounded-2xl shadow-lg border border-outline-variant/15 py-2 min-w-[180px] max-w-[240px] animate-fade-in overflow-hidden"
        style={{ left: x, top: y }}
      >
        {items.map((item, index) => (
          <button
            key={index}
            onClick={() => {
              item.onClick();
              onClose();
            }}
            className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-sans transition-colors cursor-pointer ${
              item.danger
                ? 'text-error hover:bg-error/10'
                : 'text-on-surface hover:bg-surface-container'
            }`}
          >
            <span
              className={`material-symbols-outlined text-[18px] ${
                item.danger ? 'text-error' : 'text-on-surface-variant'
              }`}
            >
              {item.icon}
            </span>
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </div>
    </>
  );
}