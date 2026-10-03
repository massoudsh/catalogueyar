import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  ApiError,
  generateCatalog,
  getDraft,
  listHistory,
  updateDraft,
} from "../lib/api";
import type { CatalogDraft, CatalogGenerateResponse } from "../lib/schemas";
import { CatalogEditor } from "../components/CatalogEditor";
import {
  GeneratePanel,
  type GenerateSubmitPayload,
} from "../components/GeneratePanel";
import { HistoryList } from "../components/HistoryList";
import { StatusBanner } from "../components/StatusBanner";

export function WorkspacePage() {
  const [catalog, setCatalog] = useState<CatalogGenerateResponse | null>(null);
  const [draftId, setDraftId] = useState<string | null>(null);
  const [history, setHistory] = useState<CatalogDraft[]>([]);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<{
    message: string;
    tone: "neutral" | "ok" | "error" | "warn";
  }>({
    message: "آماده دریافت اطلاعات محصول.",
    tone: "neutral",
  });

  const refreshHistory = useCallback(async () => {
    try {
      const drafts = await listHistory();
      setHistory(drafts);
    } catch {
      /* history is optional for first-run UX */
    }
  }, []);

  useEffect(() => {
    void refreshHistory();
  }, [refreshHistory]);

  async function handleGenerate(payload: GenerateSubmitPayload) {
    setBusy(true);
    setStatus({ message: "در حال تولید کاتالوگ…", tone: "neutral" });
    try {
      const result = await generateCatalog({
        images: payload.images,
        voiceNote: payload.voiceNote,
        sellerHint: payload.sellerHint,
        storeCategories: payload.storeCategories,
      });
      setCatalog(result);
      setDraftId(result.draft_id ?? null);
      setStatus({
        message: result.draft_id
          ? "کاتالوگ ساخته شد. می‌توانی فیلدها را ویرایش و ذخیره کنی."
          : "کاتالوگ ساخته شد.",
        tone: "ok",
      });
      await refreshHistory();
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "ارتباط با سرور برقرار نشد. بک‌اند را روی پورت ۸۰۰۰ اجرا کن.";
      setStatus({ message, tone: "error" });
    } finally {
      setBusy(false);
    }
  }

  async function handleSave(next: CatalogGenerateResponse) {
    if (!draftId) return;
    setBusy(true);
    setStatus({ message: "در حال ذخیرهٔ اصلاحات…", tone: "neutral" });
    try {
      const updated = await updateDraft(draftId, {
        title: next.title,
        description: next.description,
        category: next.category,
        attributes: next.attributes,
        variants: next.variants,
        missing_info_questions: next.missing_info_questions,
        english: next.english ?? undefined,
      });
      setCatalog({ ...updated.catalog, draft_id: updated.id });
      setDraftId(updated.id);
      setStatus({
        message: "اصلاحات ذخیره شد و در یادگیری بعدی فروشنده استفاده می‌شود.",
        tone: "ok",
      });
      await refreshHistory();
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "ذخیرهٔ اصلاحات ناموفق بود.";
      setStatus({ message, tone: "error" });
      throw error;
    } finally {
      setBusy(false);
    }
  }

  async function handleSelectDraft(draft: CatalogDraft) {
    setBusy(true);
    setStatus({ message: "در حال بارگذاری draft…", tone: "neutral" });
    try {
      const fresh = await getDraft(draft.id);
      setCatalog({ ...fresh.catalog, draft_id: fresh.id });
      setDraftId(fresh.id);
      setStatus({ message: "draft بارگذاری شد.", tone: "ok" });
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "بارگذاری draft ناموفق بود.";
      setStatus({ message, tone: "error" });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-6xl px-5 pb-20 pt-4 md:px-8">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 max-w-2xl"
      >
        <p className="font-display text-3xl font-bold text-teal sm:text-4xl">
          CatalogYar
        </p>
        <h1 className="mt-2 text-2xl font-extrabold text-ink">فضای ساخت و ویرایش</h1>
        <p className="mt-2 text-sm leading-7 text-ink-soft/85">
          رسانه را بفرست، خروجی را ببین، فیلدهای کم‌اطمینان را اصلاح کن.
        </p>
      </motion.div>

      <div className="mb-5">
        <StatusBanner message={status.message} tone={status.tone} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)]">
        <div className="space-y-4">
          <GeneratePanel busy={busy} onSubmit={handleGenerate} />
          <HistoryList
            drafts={history}
            activeId={draftId}
            onSelect={(draft) => void handleSelectDraft(draft)}
            onRefresh={() => void refreshHistory()}
            busy={busy}
          />
        </div>
        <CatalogEditor
          catalog={catalog}
          draftId={draftId}
          busy={busy}
          onSave={handleSave}
        />
      </div>
    </main>
  );
}
