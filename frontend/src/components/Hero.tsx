import { Link } from "react-router-dom";
import { motion } from "framer-motion";

export function Hero() {
  return (
    <section className="relative mx-auto flex min-h-[calc(100vh-5.5rem)] w-full max-w-6xl flex-col justify-center px-5 pb-16 pt-6 md:px-8 md:pb-24">
      <div className="pointer-events-none absolute inset-x-0 top-8 -z-0 h-[70%] overflow-hidden md:top-0">
        <motion.div
          initial={{ opacity: 0, scale: 1.04 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.1, ease: "easeOut" }}
          className="absolute inset-0 bg-[radial-gradient(ellipse_at_70%_40%,rgba(15,92,86,0.22),transparent_58%),radial-gradient(ellipse_at_20%_70%,rgba(232,163,23,0.18),transparent_50%)]"
          aria-hidden
        />
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 0.55, y: 0 }}
          transition={{ delay: 0.2, duration: 1 }}
          className="absolute bottom-0 left-1/2 h-[55%] w-[120%] -translate-x-1/2 rounded-[100%] bg-gradient-to-t from-teal/25 via-teal/5 to-transparent blur-2xl"
          aria-hidden
        />
      </div>

      <div className="relative z-10 max-w-3xl">
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="font-display text-5xl font-bold leading-none tracking-tight text-teal sm:text-6xl md:text-7xl"
        >
          CatalogYar
          <span className="mt-3 block font-body text-2xl font-extrabold text-ink sm:text-3xl md:text-4xl">
            کاتالوگ‌یار
          </span>
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.12, duration: 0.55 }}
          className="mt-8 max-w-2xl text-2xl font-bold leading-snug text-ink sm:text-3xl"
        >
          از عکس، ویدئو و ویس؛ کاتالوگ آماده فروش بساز.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.22, duration: 0.55 }}
          className="mt-4 max-w-xl text-base leading-8 text-ink-soft/85 sm:text-lg"
        >
          به‌جای پرکردن فرم، محصولت را نشان بده — عنوان، دسته، توضیح و ویژگی‌ها را
          می‌سازیم؛ بعد در حالت ویرایش اصلاح کن.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.34, duration: 0.55 }}
          className="mt-9 flex flex-wrap items-center gap-3"
        >
          <Link
            to="/workspace"
            className="inline-flex items-center justify-center rounded-xl bg-teal px-6 py-3 text-sm font-bold text-paper shadow-[0_12px_30px_-12px_rgba(15,92,86,0.65)] transition hover:bg-teal-bright"
          >
            شروع ساخت کاتالوگ
          </Link>
          <a
            href="#how"
            className="inline-flex items-center justify-center rounded-xl px-5 py-3 text-sm font-semibold text-teal underline-offset-4 hover:underline"
          >
            چطور کار می‌کند؟
          </a>
        </motion.div>
      </div>
    </section>
  );
}
