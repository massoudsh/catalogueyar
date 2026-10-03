import { Link, NavLink } from "react-router-dom";
import { motion } from "framer-motion";

type SiteHeaderProps = {
  apiOnline?: boolean | null;
};

export function SiteHeader({ apiOnline = null }: SiteHeaderProps) {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    [
      "text-sm transition-colors",
      isActive ? "text-teal font-semibold" : "text-ink-soft/80 hover:text-teal",
    ].join(" ");

  return (
    <motion.header
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
      className="mx-auto flex w-full max-w-6xl items-center justify-between px-5 py-5 md:px-8"
    >
      <Link to="/" className="group flex items-baseline gap-2">
        <span className="font-display text-2xl font-bold tracking-tight text-teal md:text-3xl">
          CatalogYar
        </span>
        <span className="text-sm font-semibold text-ink-soft/70 group-hover:text-teal transition-colors">
          کاتالوگ‌یار
        </span>
      </Link>

      <nav className="flex items-center gap-5">
        <NavLink to="/" end className={linkClass}>
          خانه
        </NavLink>
        <NavLink to="/workspace" className={linkClass}>
          ساخت کاتالوگ
        </NavLink>
        {apiOnline !== null && (
          <span
            className={[
              "hidden sm:inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs",
              apiOnline
                ? "bg-teal/10 text-teal"
                : "bg-danger/10 text-danger",
            ].join(" ")}
            title={apiOnline ? "API در دسترس است" : "API در دسترس نیست"}
          >
            <span
              className={[
                "size-1.5 rounded-full",
                apiOnline ? "bg-ok" : "bg-danger",
              ].join(" ")}
            />
            {apiOnline ? "API" : "آفلاین"}
          </span>
        )}
      </nav>
    </motion.header>
  );
}
