import { z } from "zod";

export const AttributeSchema = z.object({
  name: z.string(),
  value: z.string(),
  confidence: z.number().min(0).max(1),
});

export const VariantSchema = z.object({
  type: z.string(),
  options: z.array(z.string()),
});

export const CategorySchema = z.object({
  suggested: z.string(),
  confidence: z.number().min(0).max(1),
});

export const SourceEvidenceSchema = z.object({
  from_image: z.array(z.string()).default([]),
  from_voice: z.array(z.string()).default([]),
  from_text_on_package: z.array(z.string()).default([]),
});

export const EnglishCatalogSchema = z.object({
  title: z.string().default(""),
  description: z.string().default(""),
  attributes: z.array(AttributeSchema).default([]),
});

export const CatalogGenerateResponseSchema = z.object({
  title: z.string(),
  category: CategorySchema,
  description: z.string(),
  attributes: z.array(AttributeSchema),
  variants: z.array(VariantSchema),
  missing_info_questions: z.array(z.string()),
  source_evidence: SourceEvidenceSchema,
  english: EnglishCatalogSchema.nullable().optional(),
  draft_id: z.string().nullable().optional(),
});

export const CatalogDraftSchema = z.object({
  id: z.string(),
  seller_id: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  catalog: CatalogGenerateResponseSchema,
});

export const CatalogUpdateSchema = z.object({
  title: z.string().optional(),
  description: z.string().optional(),
  category: CategorySchema.optional(),
  attributes: z.array(AttributeSchema).optional(),
  variants: z.array(VariantSchema).optional(),
  missing_info_questions: z.array(z.string()).optional(),
  english: EnglishCatalogSchema.optional(),
});

export const HealthSchema = z.object({
  status: z.string(),
});

export const GenerateFormSchema = z.object({
  mediaCount: z
    .number()
    .int()
    .min(1, "حداقل یک عکس یا ویدئو لازم است")
    .max(5, "حداکثر ۵ رسانه مجاز است"),
  sellerHint: z.string().max(2000).optional(),
  categories: z.string().optional(),
});

export type Attribute = z.infer<typeof AttributeSchema>;
export type Variant = z.infer<typeof VariantSchema>;
export type Category = z.infer<typeof CategorySchema>;
export type CatalogGenerateResponse = z.infer<typeof CatalogGenerateResponseSchema>;
export type CatalogDraft = z.infer<typeof CatalogDraftSchema>;
export type CatalogUpdate = z.infer<typeof CatalogUpdateSchema>;
