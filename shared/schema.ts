import { pgTable, serial, text, timestamp, boolean, integer, numeric } from "drizzle-orm/pg-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  email: text("email").unique(),
  password: text("password").notNull(),
  role: text("role").default("user"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const tradingAccounts = pgTable("trading_accounts", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  broker: text("broker").notNull(),
  accountNumber: text("account_number").notNull(),
  balance: numeric("balance").notNull(),
  currency: text("currency").default("USD"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const positions = pgTable("positions", {
  id: serial("id").primaryKey(),
  accountId: integer("account_id").references(() => tradingAccounts.id),
  symbol: text("symbol").notNull(),
  side: text("side").notNull(),
  size: numeric("size").notNull(),
  entryPrice: numeric("entry_price").notNull(),
  currentPrice: numeric("current_price"),
  status: text("status").default("open"),
  openTime: timestamp("open_time").defaultNow(),
  closeTime: timestamp("close_time"),
  pnl: numeric("pnl"),
});

export const notifications = pgTable("notifications", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  title: text("title").notNull(),
  message: text("message").notNull(),
  type: text("type").default("info"),
  read: boolean("read").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

export const educationalResources = pgTable("educational_resources", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  skillLevel: text("skill_level"),
  category: text("category"),
  resourceType: text("resource_type"),
  content: text("content"),
  imageUrl: text("image_url"),
  featured: boolean("featured").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

// Zod Schemas
export const insertUserSchema = createInsertSchema(users);
export const selectUserSchema = createSelectSchema(users);
export const insertAccountSchema = createInsertSchema(tradingAccounts);
export const selectAccountSchema = createSelectSchema(tradingAccounts);
export const insertPositionSchema = createInsertSchema(positions);
export const selectPositionSchema = createSelectSchema(positions);
export const insertNotificationSchema = createInsertSchema(notifications);
export const selectNotificationSchema = createSelectSchema(notifications);
export const insertResourceSchema = createInsertSchema(educationalResources);
export const selectResourceSchema = createSelectSchema(educationalResources);

export const resourceSchema = selectResourceSchema;
export type Resource = z.infer<typeof resourceSchema>;
export type InsertResource = z.infer<typeof insertResourceSchema>;

// Query filters schema
export const resourceFiltersSchema = z.object({
  search: z.string().optional(),
  skillLevel: z.enum(["beginner", "intermediate", "advanced"]).optional(),
  category: z.enum(["programming", "design", "marketing", "data-science"]).optional(),
  resourceType: z.enum(["video", "article", "course", "tutorial"]).optional(),
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().max(50).default(12),
});

export type ResourceFilters = z.infer<typeof resourceFiltersSchema>;

// Response schema for paginated resources
export const resourcesResponseSchema = z.object({
  resources: z.array(resourceSchema),
  totalCount: z.number(),
  totalPages: z.number(),
  currentPage: z.number(),
  hasNextPage: z.boolean(),
  hasPrevPage: z.boolean(),
});

export type ResourcesResponse = z.infer<typeof resourcesResponseSchema>;
