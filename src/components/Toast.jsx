import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Toast({ message, type = 'info', duration = 3000, onClose }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      if (onClose) onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!visible) return null;

  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <XCircle className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />
  };

  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500'
  };

  return (
    <div className={`fixed bottom-8 right-8 ${colors[type]} text-white px-6 py-4 rounded-lg shadow-2xl flex items-center space-x-3 animate-slide-up z-50 max-w-md`}>
      {icons[type]}
      <p className="text-sm font-medium">{message}</p>
      <button
        onClick={() => {
          setVisible(false);
          if (onClose) onClose();
        }}
        className="ml-4 hover:bg-white/20 rounded p-1"
      >
        ×
      </button>
    </div>
  );
}
