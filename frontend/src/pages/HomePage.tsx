import { motion } from "framer-motion";
import { Hero } from "../components/Hero";

export function HomePage() {
  return (
    <>
      <Hero />
      <section
        id="how"
        className="mx-auto w-full max-w-6xl px-5 pb-20 md:px-8"
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl"
        >
          <h2 className="text-2xl font-bold text-ink">یک مسیر ساده تا کاتالوگ</h2>
          <p className="mt-3 text-sm leading-8 text-ink-soft/85 sm:text-base">
            رسانه محصول را بفرست؛ موتور vision و speech شواهد را استخراج می‌کند،
            متن فروشگاهی فارسی (و در صورت امکان انگلیسی) می‌سازد، draft را ذخیره
            می‌کند و فیلدهای کم‌اطمینان را برای ویرایش هایلایت می‌کند.
          </p>
          <ol className="mt-8 space-y-5 border-r border-teal/25 pr-5">
            {[
              "۱ تا ۵ عکس یا ویدئو + ویس اختیاری",
              "تولید عنوان، دسته، توضیح و ویژگی‌ها",
              "ویرایش فیلدها و ذخیرهٔ feedback برای یادگیری بعدی",
            ].map((step) => (
              <li key={step} className="text-sm font-medium leading-7 text-ink-soft">
                {step}
              </li>
            ))}
          </ol>
        </motion.div>
      </section>
    </>
  );
}
