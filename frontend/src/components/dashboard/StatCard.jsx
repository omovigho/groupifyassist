import { motion } from 'framer-motion';

const StatCard = ({ title, value, icon: Icon, color='#0A2540' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
  className="rounded-2xl bg-white dark:bg-slate-900 shadow-sm border border-slate-200 dark:border-slate-800 p-5"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-500 dark:text-slate-400 text-sm">{title}</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-100">{value}</p>
        </div>
        {Icon ? (
          <div className="h-10 w-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}1A` }}>
            <Icon size={20} style={{ color }} />
          </div>
        ) : null}
      </div>
    </motion.div>
  );
};

export default StatCard;
