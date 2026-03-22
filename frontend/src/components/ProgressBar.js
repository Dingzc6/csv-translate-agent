import React from 'react';
import { motion } from 'framer-motion';
import { Check, Loader2, Clock } from 'lucide-react';

const STATUS_CONFIG = {
  pending: { icon: Clock, color: 'slate', label: '等待中' },
  translating: { icon: Loader2, color: 'indigo', label: '翻译中', animate: true },
  validating: { icon: Loader2, color: 'violet', label: '校验中', animate: true },
  completed: { icon: Check, color: 'emerald', label: '已完成' },
  failed: { icon: null, color: 'red', label: '失败' },
};

function ProgressBar({ darkMode, progress, totalBatches, currentBatch }) {
  const total = totalBatches || progress?.total_batches || 1;
  const completed = progress?.completed_batches || 0;
  const percent = Math.round((completed / total) * 100);
  const currentStatus = progress?.status || 'pending';

  // Generate batch status array
  const batches = Array.from({ length: total }, (_, i) => {
    if (i < completed) return 'completed';
    if (i === currentBatch) return currentStatus;
    return 'pending';
  });

  return (
    <div className="w-full space-y-4">
      {/* Progress Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-display font-bold ${
            darkMode ? 'text-white' : 'text-slate-800'
          }`}>
            {percent}%
          </span>
          <span className={`text-sm ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            完成
          </span>
        </div>

        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
          darkMode ? 'bg-slate-700/50 text-slate-300' : 'bg-slate-100 text-slate-600'
        }`}>
          <span className={`font-medium ${
            currentStatus === 'translating' ? 'text-indigo-500' :
            currentStatus === 'validating' ? 'text-violet-500' :
            currentStatus === 'completed' ? 'text-emerald-500' : ''
          }`}>
            {STATUS_CONFIG[currentStatus]?.label || '准备中'}
          </span>
        </div>
      </div>

      {/* Segmented Progress */}
      <div className="flex gap-1.5">
        {batches.map((status, index) => {
          const config = STATUS_CONFIG[status];
          const Icon = config?.icon;

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, scaleX: 0 }}
              animate={{ opacity: 1, scaleX: 1 }}
              transition={{ delay: index * 0.05 }}
              className={`progress-segment relative ${status}`}
              style={{ transformOrigin: 'left' }}
            >
              <div
                className={`progress-segment-fill ${
                  status === 'completed' ? 'bg-emerald-500' :
                  status === 'translating' ? 'bg-gradient-to-r from-indigo-500 to-violet-500' :
                  status === 'validating' ? 'bg-gradient-to-r from-violet-500 to-purple-500' :
                  status === 'failed' ? 'bg-red-500' : ''
                }`}
                style={{
                  width: status === 'pending' ? '0%' : '100%'
                }}
              />

              {/* Batch indicator */}
              {status !== 'pending' && status !== 'completed' && (
                <motion.div
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="absolute inset-0 flex items-center justify-center"
                >
                  {Icon && (
                    <Icon
                      className={`w-3 h-3 text-white ${config.animate ? 'animate-spin' : ''}`}
                    />
                  )}
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Batch Counter */}
      <div className={`flex items-center justify-between text-xs ${
        darkMode ? 'text-slate-500' : 'text-slate-400'
      }`}>
        <span>Batch {completed + (currentStatus !== 'completed' ? 1 : 0)} / {total}</span>
        <span>{completed} 批次已完成</span>
      </div>

      {/* Status Details */}
      {currentStatus === 'validating' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-3 rounded-xl text-sm ${
            darkMode ? 'bg-violet-500/10 text-violet-300' : 'bg-violet-50 text-violet-700'
          }`}
        >
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>正在校验翻译质量...</span>
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default ProgressBar;
